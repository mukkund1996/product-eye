from crewai.tools import tool
from langchain_community.tools.playwright import (
    ClickTool,
    NavigateTool,
    ExtractTextTool,
    GetElementsTool,
    CurrentWebPageTool,
    NavigateBackTool,
)
from langchain_community.tools.playwright.utils import create_sync_playwright_browser


class PlaywrightToolsWrapper:
    """Wrapper class for Playwright tools to make them compatible with CrewAI."""

    def __init__(self, headless: bool = False):
        """Initialize the browser with optimized settings for clicking."""
        self.headless = headless

        # Create browser with better configurations
        self.sync_browser = create_sync_playwright_browser(headless=headless)

        # Create context with better settings
        context = self.sync_browser.new_context(
            # Disable security features that might block clicks
            bypass_csp=True,
            ignore_https_errors=True,
            # Set realistic viewport
            viewport={"width": 1280, "height": 720},
            # Add user agent to avoid bot detection
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        self._current_page = context.new_page()

        # Set longer default timeouts
        self._current_page.set_default_timeout(10000)  # 10 seconds
        self._current_page.set_default_navigation_timeout(30000)  # 30 seconds

        # Initialize community tools with the browser
        self._navigate_tool = NavigateTool(sync_browser=self.sync_browser)
        self._click_tool = ClickTool(sync_browser=self.sync_browser)
        self._extract_text_tool = ExtractTextTool(sync_browser=self.sync_browser)
        self._get_elements_tool = GetElementsTool(sync_browser=self.sync_browser)
        self._current_page_tool = CurrentWebPageTool(sync_browser=self.sync_browser)
        self._navigate_back_tool = NavigateBackTool(sync_browser=self.sync_browser)

    def get_navigate_tool(self):
        """Get the wrapped navigate tool using community tool."""

        @tool("Navigate to URL")
        def navigate_to_url(url: str) -> str:
            """Navigate to a specific URL using langchain community tool."""
            try:
                result = self._navigate_tool.run(url)

                # Get additional info for better feedback
                page = self._get_current_page()
                current_url = page.url
                title = page.title()

                return f"{result}\nCurrent URL: {current_url}\nPage Title: {title}"
            except Exception as e:
                return f"Navigation failed: {str(e)}"

        return navigate_to_url

    def get_click_tool(self):
        """Get the click tool using community tool."""

        @tool("Click Element")
        def click_element(selector: str) -> str:
            """
            Click on an element using CSS selector with community tool.
            Validates selector exists before clicking.
            """
            try:
                page = self._get_current_page()
                current_url = page.url
                initial_url = page.url

                # STEP 1: Validate selector exists first
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
                                f"Try: 'a[class*=\"{selector.split('.')[1]}\"]' for partial class match"
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

                except Exception as e:
                    return f"❌ Invalid selector '{selector}': {str(e)}\n💡 Try using basic selectors like 'a', 'button', 'input'"

                # Use community click tool
                try:
                    result = self._click_tool.run(selector)

                    # Check if navigation occurred
                    try:
                        page.wait_for_load_state("networkidle", timeout=3000)
                    except:
                        pass

                    final_url = page.url
                    if initial_url != final_url:
                        return f"✅ Clicked: {selector}\n📍 Navigated from {initial_url} to {final_url}"
                    else:
                        return f"✅ Clicked: {selector} (stayed on same page)"

                except Exception as e:
                    return f"❌ Click failed: {str(e)}\n💡 Try using 'Discover Clickable Elements' to find working selectors"

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
        """Get tool to extract text content using community tool."""

        @tool("Extract Text")
        def extract_text(selector: str = "") -> str:
            """Extract text from the page or specific element using community ExtractTextTool."""
            try:
                page = self._get_current_page()
                current_url = page.url

                if not selector or selector == "":
                    # Use current page tool for full page info
                    try:
                        result = self._current_page_tool.run()
                        return f"📄 Current Page Info:\n{result}"
                    except Exception as e:
                        return f"❌ Error getting page info: {str(e)}"
                else:
                    # Use community extract text tool
                    try:
                        # Validate selector exists first
                        elements = page.locator(selector).all()
                        if not elements:
                            return f"❌ No elements found with selector: {selector} on {current_url}"

                        result = self._extract_text_tool.run(selector)
                        return f"🌐 URL: {current_url}\n📝 Extracted text: {result}"

                    except Exception as e:
                        return f"❌ Error extracting text: {str(e)}"

            except Exception as e:
                return f"❌ Error in extract_text: {str(e)}"

        return extract_text

    def get_elements_tool(self):
        """Get tool to find elements using community tool."""

        @tool("Get Elements")
        def get_elements(selector: str) -> str:
            """Get elements matching the CSS selector using community GetElementsTool."""
            try:
                page = self._get_current_page()
                current_url = page.url

                # Use community get elements tool
                try:
                    result = self._get_elements_tool.run(selector)
                    return f"🌐 URL: {current_url}\n📋 Elements found: {result}"
                except Exception as e:
                    return f"❌ Error getting elements: {str(e)}"

            except Exception as e:
                return f"Error in get_elements: {str(e)}"

        return get_elements

    def get_current_page_tool(self):
        """Get tool for current page info using community tool."""

        @tool("Get Current Page")
        def get_current_page() -> str:
            """Get comprehensive information about the current web page using community CurrentWebPageTool."""
            try:
                # Use community current page tool
                try:
                    result = self._current_page_tool.run()
                    return f"📄 Current Page Info:\n{result}"
                except Exception as e:
                    return f"❌ Error getting current page info: {str(e)}"

            except Exception as e:
                return f"❌ Error getting current page info: {str(e)}"

        return get_current_page

    def get_navigate_back_tool(self):
        """Get tool for back navigation using community tool."""

        @tool("Navigate Back")
        def navigate_back() -> str:
            """Navigate back to the previous page using community NavigateBackTool."""
            try:
                # Use community navigate back tool
                try:
                    result = self._navigate_back_tool.run()
                    page = self._get_current_page()
                    new_url = page.url
                    return f"✅ Back navigation: {result}\n📍 Current URL: {new_url}"
                except Exception as e:
                    return f"❌ Navigate back failed: {str(e)}"

            except Exception as e:
                return f"❌ Error in navigate_back: {str(e)}"

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
            self.get_discover_elements_tool(),  # Keep custom discover tool for enhanced element finding
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
