import tempfile
import os
from playwright.sync_api import sync_playwright
from PIL import Image
import io

def react_to_screenshot(react_code: str, width: int = 1920) -> Image.Image:
    """
    Takes React code as a string, bundles it into an HTML file, 
    and returns a screenshot as a PIL Image in 16:9 aspect ratio.
    
    Args:
        react_code: React JSX code as a string
        width: Screenshot width (height auto-calculated for 16:9)
    
    Returns:
        PIL Image of the rendered React component
    """
    # Force 16:9 aspect ratio
    height = int(width * 9 / 16)
    
    # HTML template with React setup
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>React Screenshot</title>
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: white;
            }}
            #root {{
                width: 100%;
                height: 100vh;
            }}
        </style>
    </head>
    <body>
        <div id="root"></div>
        
        <script type="text/babel">
            {react_code}
            
            // Auto-render if there's a default export or App component
            const rootElement = document.getElementById('root');
            const root = ReactDOM.createRoot(rootElement);
            
            if (typeof App !== 'undefined') {{
                root.render(React.createElement(App));
            }} else if (typeof module !== 'undefined' && module.exports) {{
                root.render(React.createElement(module.exports.default || module.exports));
            }} else {{
                // Try to find any React component in the global scope
                const componentNames = Object.keys(window).filter(key => 
                    typeof window[key] === 'function' && 
                    key[0] === key[0].toUpperCase()
                );
                if (componentNames.length > 0) {{
                    root.render(React.createElement(window[componentNames[0]]));
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    # Create temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_template)
        temp_file_path = f.name
    
    try:
        # Use Playwright to take screenshot
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": width, "height": height})
            
            # Load the HTML file
            page.goto(f"file://{temp_file_path}")
            
            # Wait for React to render
            page.wait_for_timeout(2000)
            
            # Take screenshot
            screenshot_bytes = page.screenshot(full_page=False)
            browser.close()
            
        # Convert to PIL Image
        image = Image.open(io.BytesIO(screenshot_bytes))
        return image
        
    finally:
        # Clean up temp file
        os.unlink(temp_file_path)

def save_screenshot(react_code: str, output_path: str, width: int = 1920):
    """
    Convenience function to save screenshot directly to file.
    """
    image = react_to_screenshot(react_code, width)
    image.save(output_path)
    return image

if __name__ == "__main__":
    # Demo usage
    demo_react = """
    function App() {
        const [count, setCount] = React.useState(0);
        
        return (
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100vh',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                textAlign: 'center'
            }}>
                <h1 style={{ fontSize: '4rem', marginBottom: '2rem' }}>
                    React Screenshot Demo
                </h1>
                <p style={{ fontSize: '1.5rem', marginBottom: '2rem' }}>
                    Count: {count}
                </p>
                <button
                    onClick={() => setCount(count + 1)}
                    style={{
                        fontSize: '1.2rem',
                        padding: '1rem 2rem',
                        border: 'none',
                        borderRadius: '8px',
                        background: 'rgba(255,255,255,0.2)',
                        color: 'white',
                        cursor: 'pointer',
                        backdropFilter: 'blur(10px)'
                    }}
                >
                    Click Me!
                </button>
            </div>
        );
    }
    """
    
    print("Taking screenshot of React demo...")
    image = react_to_screenshot(demo_react)
    image.save("react_demo_screenshot.png")
    print("Screenshot saved as react_demo_screenshot.png")
