"""
Demo React components for testing the screenshot utility.
"""

# Simple counter component
COUNTER_COMPONENT = """
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
            fontFamily: 'Arial, sans-serif'
        }}>
            <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                React Counter
            </h1>
            <div style={{ 
                fontSize: '2rem', 
                marginBottom: '2rem',
                padding: '1rem',
                background: 'rgba(255,255,255,0.1)',
                borderRadius: '10px'
            }}>
                Count: {count}
            </div>
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
                    transition: 'all 0.3s ease'
                }}
            >
                Increment
            </button>
        </div>
    );
}
"""

# Card layout component
CARD_LAYOUT = """
function App() {
    const cards = [
        { title: "Card 1", content: "This is the first card", color: "#ff6b6b" },
        { title: "Card 2", content: "This is the second card", color: "#4ecdc4" },
        { title: "Card 3", content: "This is the third card", color: "#45b7d1" },
        { title: "Card 4", content: "This is the fourth card", color: "#96ceb4" }
    ];
    
    return (
        <div style={{
            padding: '2rem',
            background: 'linear-gradient(45deg, #f0f2f0 0%, #f8f9fa 100%)',
            minHeight: '100vh'
        }}>
            <h1 style={{
                textAlign: 'center',
                color: '#333',
                marginBottom: '3rem',
                fontSize: '2.5rem'
            }}>
                React Card Layout Demo
            </h1>
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '2rem',
                maxWidth: '800px',
                margin: '0 auto'
            }}>
                {cards.map((card, index) => (
                    <div
                        key={index}
                        style={{
                            background: card.color,
                            padding: '2rem',
                            borderRadius: '12px',
                            color: 'white',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                            transition: 'transform 0.3s ease'
                        }}
                    >
                        <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.5rem' }}>
                            {card.title}
                        </h3>
                        <p style={{ margin: 0, opacity: 0.9 }}>
                            {card.content}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
}
"""

# Dashboard component
DASHBOARD_COMPONENT = """
function App() {
    const stats = [
        { label: "Users", value: "10,234", change: "+12%" },
        { label: "Revenue", value: "$45,678", change: "+8%" },
        { label: "Orders", value: "892", change: "+23%" },
        { label: "Conversion", value: "3.2%", change: "+0.5%" }
    ];
    
    return (
        <div style={{
            background: '#f8fafc',
            minHeight: '100vh',
            padding: '2rem'
        }}>
            <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                <header style={{ marginBottom: '3rem' }}>
                    <h1 style={{
                        color: '#1a202c',
                        fontSize: '2.5rem',
                        marginBottom: '0.5rem'
                    }}>
                        Analytics Dashboard
                    </h1>
                    <p style={{ color: '#718096', fontSize: '1.1rem' }}>
                        Welcome back! Here's what's happening with your business.
                    </p>
                </header>
                
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(4, 1fr)',
                    gap: '1.5rem',
                    marginBottom: '3rem'
                }}>
                    {stats.map((stat, index) => (
                        <div
                            key={index}
                            style={{
                                background: 'white',
                                padding: '1.5rem',
                                borderRadius: '8px',
                                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                                borderLeft: '4px solid #4299e1'
                            }}
                        >
                            <div style={{ color: '#718096', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                                {stat.label}
                            </div>
                            <div style={{ color: '#1a202c', fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                                {stat.value}
                            </div>
                            <div style={{ color: '#38a169', fontSize: '0.9rem' }}>
                                {stat.change} from last month
                            </div>
                        </div>
                    ))}
                </div>
                
                <div style={{
                    background: 'white',
                    padding: '2rem',
                    borderRadius: '8px',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                }}>
                    <h2 style={{ color: '#1a202c', marginBottom: '1rem' }}>Recent Activity</h2>
                    <div style={{ color: '#718096' }}>
                        Chart and activity feed would go here...
                    </div>
                </div>
            </div>
        </div>
    );
}
"""

if __name__ == "__main__":
    from react_screenshot import react_to_screenshot
    
    print("Testing demo React components...")
    
    # Test each component
    components = [
        ("counter", COUNTER_COMPONENT),
        ("cards", CARD_LAYOUT),
        ("dashboard", DASHBOARD_COMPONENT)
    ]
    
    for name, component in components:
        print(f"Generating screenshot for {name}...")
        image = react_to_screenshot(component)
        filename = f"demo_{name}_screenshot.png"
        image.save(filename)
        print(f"Saved {filename}")
