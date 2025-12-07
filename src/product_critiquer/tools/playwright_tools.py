from crewai.tools import tool
from langchain_community.tools.playwright.utils import create_sync_playwright_browser


class PlaywrightToolsWrapper:
    """Wrapper class for Playwright tools to make them compatible with CrewAI."""

    def __init__(self, headless: bool = False):
        """Initialize the browser and create wrapped tools."""
        self.headless = headless
        self.sync_browser = create_sync_playwright_browser(headless=headless)
        self._current_page = None
        self._ensure_page()

    def get_navigate_tool(self):
        """Get the wrapped navigate tool."""

        @tool("Navigate to URL")
        def navigate_to_url(url: str) -> str:
            """Navigate to a specific URL and maintain browser state."""
            try:
                page = self._get_current_page()
                page.goto(url, timeout=30000)

                # Wait for page to load
                page.wait_for_load_state("networkidle", timeout=10000)

                current_url = page.url
                title = page.title()

                return f"Successfully navigated to: {current_url}\nPage Title: {title}"

            except Exception as e:
                return f"Navigation failed: {str(e)}"

        return navigate_to_url

    def get_click_tool(self):
        """Get the enhanced click tool with generic element validation."""

        @tool("Click Element")
        def click_element(selector: str) -> str:
            """
            Click on an element using CSS selector with validation and multiple fallback strategies.
            First validates the selector exists, then tries various clicking approaches.
            """
            try:
                page = self._get_current_page()
                current_url = page.url

                # STEP 1: Validate selector exists
                try:
                    elements = page.locator(selector).all()
                    if not elements:
                        # Generic suggestions based on common selector patterns
                        suggestions = []

                        if selector.startswith(".") and "link" in selector.lower():
                            suggestions.append("Try: 'a' for all links")
                            suggestions.append(
                                "Try: 'a[href]' for links with href attribute"
                            )
                        elif "storylink" in selector or "title" in selector:
                            suggestions.append("Try: 'a' for links")
                            suggestions.append(
                                "Try: 'h1 a, h2 a, h3 a' for title links"
                            )
                        elif selector.startswith("a.") and selector != "a":
                            suggestions.append(f"Try: 'a' instead of '{selector}'")
                            suggestions.append(
                                "Try: 'a[class*=\"{}\"]' for partial class match".format(
                                    selector.split(".")[1]
                                )
                            )
                        elif "button" in selector.lower():
                            suggestions.append("Try: 'button' for all buttons")
                            suggestions.append(
                                'Try: \'input[type="submit"], input[type="button"]\' for input buttons'
                            )
                        else:
                            suggestions.append(
                                "Use 'Discover Clickable Elements' tool to find available selectors"
                            )
                            suggestions.append(
                                "Try simpler selectors like 'a', 'button', 'input'"
                            )

                        suggestion_text = (
                            "\n💡 Suggestions:\n"
                            + "\n".join(f"   - {s}" for s in suggestions)
                            if suggestions
                            else ""
                        )
                        return f"❌ No elements found with selector '{selector}' on {current_url}{suggestion_text}"

                    print(
                        f"✅ Found {len(elements)} element(s) with selector: {selector}"
                    )
                except Exception as e:
                    return f"❌ Invalid selector '{selector}': {str(e)}\n💡 Try using basic selectors like 'a', 'button', 'input', or use 'Discover Clickable Elements'"

                # STEP 2: Check element properties before clicking
                element = elements[0]
                try:
                    is_visible = element.is_visible()
                    is_enabled = element.is_enabled()
                    tag_name = element.evaluate("el => el.tagName")
                    text_content = (
                        element.text_content()[:50]
                        if element.text_content()
                        else "No text"
                    )

                    print(
                        f"📋 Element info - Tag: {tag_name}, Visible: {is_visible}, Enabled: {is_enabled}"
                    )
                    print(f"📝 Text: '{text_content}'")

                    # Get href for links
                    if tag_name.lower() == "a":
                        href = element.get_attribute("href")
                        if href:
                            print(f"🔗 Link href: {href}")

                except Exception as e:
                    print(f"⚠️ Could not get element properties: {e}")

                # STEP 3: Try clicking strategies
                initial_url = page.url

                # Strategy 1: Standard click with wait
                try:
                    page.wait_for_selector(selector, timeout=3000)
                    page.click(selector, timeout=5000)

                    # Check for navigation
                    try:
                        page.wait_for_load_state("networkidle", timeout=3000)
                    except:
                        pass

                    final_url = page.url
                    if initial_url != final_url:
                        return f"✅ Successfully clicked: {selector}\n📍 Navigated from {initial_url} to {final_url}"
                    else:
                        return (
                            f"✅ Successfully clicked: {selector} (stayed on same page)"
                        )

                except Exception as e1:
                    print(f"❌ Standard click failed: {e1}")

                # Strategy 2: Force click (bypasses visibility/actionability checks)
                try:
                    page.click(selector, force=True, timeout=3000)
                    try:
                        page.wait_for_load_state("networkidle", timeout=3000)
                    except:
                        pass
                    return f"✅ Successfully force-clicked: {selector}"
                except Exception as e2:
                    print(f"❌ Force click failed: {e2}")

                # Strategy 3: Scroll into view then click
                try:
                    element.scroll_into_view_if_needed()
                    element.click(timeout=3000)
                    return f"✅ Successfully clicked after scrolling: {selector}"
                except Exception as e3:
                    print(f"❌ Scroll + click failed: {e3}")

                # Strategy 4: JavaScript click
                try:
                    page.evaluate(
                        f"""
                        const element = document.querySelector('{selector}');
                        if (element) {{
                            element.click();
                            console.log('JavaScript click executed');
                        }} else {{
                            throw new Error('Element not found for JS click');
                        }}
                    """
                    )
                    try:
                        page.wait_for_load_state("networkidle", timeout=3000)
                    except:
                        pass
                    return f"✅ Successfully clicked using JavaScript: {selector}"
                except Exception as e4:
                    print(f"❌ JavaScript click failed: {e4}")

                # Strategy 5: Click by coordinates (center of element)
                try:
                    box = element.bounding_box()
                    if box:
                        x = box["x"] + box["width"] / 2
                        y = box["y"] + box["height"] / 2
                        page.mouse.click(x, y)
                        return f"✅ Successfully clicked coordinates ({x:.0f}, {y:.0f}): {selector}"
                except Exception as e5:
                    print(f"❌ Coordinate click failed: {e5}")

                # Strategy 6: Handle text-based selectors
                if ":has-text(" in selector:
                    try:
                        import re

                        text_match = re.search(r":has-text\('([^']+)'\)", selector)
                        if text_match:
                            text_content = text_match.group(1)
                            page.get_by_text(text_content, exact=False).first.click(
                                timeout=3000
                            )
                            return f"✅ Successfully clicked by text: {text_content}"
                    except Exception as e6:
                        print(f"❌ Text click failed: {e6}")

                return f"❌ All click strategies failed for: {selector}\n💡 Try using 'Discover Clickable Elements' to find working selectors"

            except Exception as e:
                return f"❌ Critical error in click_element: {str(e)}"

        return click_element

    def get_discover_elements_tool(self):
        """Get tool to discover clickable elements on any webpage."""

        @tool("Discover Clickable Elements")
        def discover_clickable_elements(element_type: str = "all") -> str:
            """
            Discover clickable elements on the current page.
            element_type options: 'links', 'buttons', 'forms', 'interactive', 'all'
            """
            try:
                page = self._get_current_page()
                current_url = page.url

                results = [f"🔍 Discovering clickable elements on: {current_url}\n"]

                # Define generic selectors for any website
                if element_type == "links":
                    selectors_to_check = {
                        "All links": "a",
                        "Links with href": "a[href]",
                        "External links": "a[href^='http']",
                        "Internal links": "a[href^='/'], a[href^='#']",
                    }
                elif element_type == "buttons":
                    selectors_to_check = {
                        "Button elements": "button",
                        "Submit inputs": "input[type='submit']",
                        "Button inputs": "input[type='button']",
                        "Reset inputs": "input[type='reset']",
                    }
                elif element_type == "forms":
                    selectors_to_check = {
                        "Form elements": "form",
                        "Text inputs": "input[type='text'], input[type='email'], input[type='password']",
                        "Textareas": "textarea",
                        "Select dropdowns": "select",
                    }
                elif element_type == "interactive":
                    selectors_to_check = {
                        "Clickable with onclick": "[onclick]",
                        "Role=button": "[role='button']",
                        "Clickable divs/spans": "div[onclick], span[onclick]",
                        "Tabindex elements": "[tabindex]:not([tabindex='-1'])",
                    }
                else:  # all
                    selectors_to_check = {
                        "Links": "a[href]",
                        "Buttons": "button",
                        "Submit/Button inputs": "input[type='submit'], input[type='button']",
                        "Clickable elements": "[onclick], [role='button']",
                        "Form inputs": "input, textarea, select",
                    }

                for description, selector in selectors_to_check.items():
                    try:
                        elements = page.locator(selector).all()
                        if elements:
                            results.append(
                                f"\n📋 {description} ({len(elements)} found):"
                            )
                            results.append(f"   CSS Selector: {selector}")

                            # Show first few examples with useful info
                            for i, element in enumerate(
                                elements[:5]
                            ):  # Show max 5 examples
                                try:
                                    tag_name = element.evaluate(
                                        "el => el.tagName"
                                    ).lower()
                                    text = element.text_content()
                                    if text:
                                        text = text.strip()[:40] + (
                                            "..." if len(text.strip()) > 40 else ""
                                        )
                                    else:
                                        text = "No text"

                                    is_visible = element.is_visible()

                                    # Get relevant attributes
                                    attrs = []
                                    if tag_name == "a":
                                        href = element.get_attribute("href")
                                        if href:
                                            attrs.append(
                                                f"href='{href[:30]}{'...' if len(href) > 30 else ''}'"
                                            )
                                    elif tag_name in ["input", "button"]:
                                        input_type = element.get_attribute("type")
                                        if input_type:
                                            attrs.append(f"type='{input_type}'")

                                    class_attr = element.get_attribute("class")
                                    if class_attr:
                                        classes = class_attr.split()[
                                            :2
                                        ]  # First 2 classes
                                        attrs.append(f"class='{' '.join(classes)}'")

                                    id_attr = element.get_attribute("id")
                                    if id_attr:
                                        attrs.append(f"id='{id_attr}'")

                                    attr_str = f" [{', '.join(attrs)}]" if attrs else ""
                                    visibility = "" if is_visible else " (hidden)"

                                    results.append(
                                        f"   {i+1}. <{tag_name}>{attr_str} '{text}'{visibility}"
                                    )

                                except Exception as elem_error:
                                    results.append(
                                        f"   {i+1}. (Could not analyze element: {elem_error})"
                                    )

                            if len(elements) > 5:
                                results.append(
                                    f"   ... and {len(elements) - 5} more elements"
                                )

                    except Exception as e:
                        results.append(f"\n❌ Error checking {description}: {str(e)}")

                # Add usage tips
                results.append("\n💡 Usage Tips:")
                results.append("   - Use the exact 'CSS Selector' shown above")
                results.append(
                    "   - For specific elements, add [class='classname'] or [id='idname']"
                )
                results.append(
                    "   - For text-based selection, try 'a:has-text(\"exact text\")'"
                )
                results.append("   - Hidden elements may not be clickable")

                return "\n".join(results)

            except Exception as e:
                return f"❌ Error in discover_clickable_elements: {str(e)}"

        return discover_clickable_elements

    def get_extract_text_tool(self):
        """Get the wrapped extract text tool with state management."""

        @tool("Extract Text")
        def extract_text(selector: str = "") -> str:
            """Extract text from the page or specific element. Maintains current page state."""
            try:
                page = self._get_current_page()

                # Always include current URL for context
                current_url = page.url

                if not selector or selector == "":
                    # Extract all text from the page
                    text = page.evaluate("() => document.body.innerText")
                    return f"Current URL: {current_url}\n\nPage Text:\n{text[:2000]}..."
                else:
                    # Extract text from specific element
                    try:
                        element = page.locator(selector).first
                        if element.count() > 0:
                            text = element.text_content()
                            return f"Current URL: {current_url}\n\nElement Text ({selector}):\n{text}"
                        else:
                            return f"Current URL: {current_url}\n\nNo elements found with selector: {selector}"
                    except Exception as e:
                        return f"Current URL: {current_url}\n\nError extracting text: {str(e)}"

            except Exception as e:
                return f"Error in extract_text: {str(e)}"

        return extract_text

    def get_elements_tool(self):
        """Get the wrapped get elements tool with state management."""

        @tool("Get Elements")
        def get_elements(selector: str) -> str:
            """Get elements matching the CSS selector from current page."""
            try:
                page = self._get_current_page()
                current_url = page.url

                elements = page.locator(selector).all()

                if not elements:
                    return f"Current URL: {current_url}\n\nNo elements found with selector: {selector}"

                results = [
                    f"Current URL: {current_url}\n\nFound {len(elements)} element(s):"
                ]

                for i, element in enumerate(elements[:10]):  # Limit to first 10
                    try:
                        tag = element.evaluate("el => el.tagName")
                        text = (
                            element.text_content()[:100]
                            if element.text_content()
                            else "No text"
                        )
                        results.append(f"{i+1}. Tag: {tag}, Text: {text}")
                    except:
                        results.append(
                            f"{i+1}. Element found but could not extract details"
                        )

                return "\n".join(results)

            except Exception as e:
                return f"Error in get_elements: {str(e)}"

        return get_elements

    def get_current_page_tool(self):
        """Get the wrapped current page tool with enhanced info."""

        @tool("Get Current Page")
        def get_current_page() -> str:
            """Get comprehensive information about the current web page."""
            try:
                page = self._get_current_page()

                url = page.url
                title = page.title()

                # Get page metrics
                try:
                    content_info = page.evaluate(
                        """() => {
                        return {
                            readyState: document.readyState,
                            links: document.querySelectorAll('a').length,
                            forms: document.querySelectorAll('form').length,
                            images: document.querySelectorAll('img').length,
                            paragraphs: document.querySelectorAll('p').length
                        };
                    }"""
                    )
                except:
                    content_info = {"readyState": "unknown"}

                return f"""Current Page Information:
                URL: {url}
                Title: {title}
                Ready State: {content_info.get('readyState', 'unknown')}
                Links: {content_info.get('links', '?')}
                Forms: {content_info.get('forms', '?')}
                Images: {content_info.get('images', '?')}
                Paragraphs: {content_info.get('paragraphs', '?')}"""

            except Exception as e:
                return f"Error getting current page info: {str(e)}"

        return get_current_page

    def get_navigate_back_tool(self):
        """Get the wrapped navigate back tool."""

        @tool("Navigate Back")
        def navigate_back() -> str:
            """Navigate back to the previous page."""
            try:
                page = self._get_current_page()

                # Check if we can go back
                try:
                    page.go_back(timeout=10000)
                    page.wait_for_load_state("networkidle", timeout=5000)

                    new_url = page.url
                    return f"Successfully navigated back to: {new_url}"

                except Exception as e:
                    return f"Cannot navigate back: {str(e)}"

            except Exception as e:
                return f"Error in navigate_back: {str(e)}"

        return navigate_back

    def get_all_tools(self):
        """Get all wrapped Playwright tools as a list."""
        return [
            self.get_navigate_tool(),
            self.get_click_tool(),
            self.get_extract_text_tool(),
            self.get_elements_tool(),
            self.get_current_page_tool(),
            self.get_navigate_back_tool(),
        ]

    def close(self):
        """Clean up browser resources."""
        try:
            if self.sync_browser:
                self.sync_browser.close()
        except:
            pass

    def _ensure_page(self):
        """Ensure we have an active page and maintain reference."""
        try:
            if not self.sync_browser.contexts:
                context = self.sync_browser.new_context()
                self._current_page = context.new_page()
            else:
                context = self.sync_browser.contexts[0]
                if not context.pages:
                    self._current_page = context.new_page()
                else:
                    self._current_page = context.pages[0]
        except Exception as e:
            print(f"Error ensuring page: {e}")
            # Recreate browser if needed
            self.sync_browser = create_sync_playwright_browser(headless=self.headless)
            context = self.sync_browser.new_context()
            self._current_page = context.new_page()

    def _get_current_page(self):
        """Get the current page, ensuring it's valid."""
        try:
            # Check if page is still valid
            if self._current_page and not self._current_page.is_closed():
                return self._current_page
            else:
                # Page was closed, get a new one
                self._ensure_page()
                return self._current_page
        except Exception:
            # Recreate page if there's any issue
            self._ensure_page()
            return self._current_page
