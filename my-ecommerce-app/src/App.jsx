import { useState, useEffect } from 'react'
import { get, post } from '@aws-amplify/api'
import { fetchAuthSession } from '@aws-amplify/auth'
import { withAuthenticator } from '@aws-amplify/ui-react'
import '@aws-amplify/ui-react/styles.css'
import './App.css'

function App({ signOut, user }) {
  const [products, setProducts] = useState([])

  // 1. Fetch products
  useEffect(() => {
    async function fetchProducts() {
      try {
        console.log('API URL:', import.meta.env.VITE_API_GATEWAY_URL);
        const restOperation = get({
          apiName: 'ECommerceAPI',
          path: '/products'
        });
        
        const { body } = await restOperation.response;
        console.log(body);
        
        const apiData = await body.json();
        
        setProducts(apiData);
      } catch (err) {
        console.error('Error fetching products:', err); // This is the error you see
      }
    }
    fetchProducts();
  }, []);

  // 2. Function to place an order
  async function placeOrder(productId) {
    console.log(`Placing order for ${productId}`);
    try {
      const { tokens } = await fetchAuthSession();
      const idToken = tokens?.idToken?.toString();

      if (!idToken) {
        throw new Error("No authentication token found.");
      }

      const restOperation = post({
        apiName: 'ECommerceAPI',
        path: '/orders',
        options: {
          body: {
            items: [{ productId: productId, quantity: 1 }],
            userId: user.signInDetails?.loginId // Use v6 user property
          },
          headers: {
            Authorization: idToken 
          }
        }
      });

      const { body } = await restOperation.response;
      const responseData = await body.json();

      alert('Order placed successfully! Order ID: ' + responseData.OrderId);
    } catch (err) {
      console.error('Error placing order:', err);
      alert('Error placing order. See console for details.');
    }
  }

  // This is the main app view after login
  return (
    <div className="app">
      <header className="header">
        <div className="nav-container">
          <div className="logo">
            <div className="logo-icon">E</div>
          </div>
          <div className="user-section">
            <span className="welcome-text">Hello, {user.signInDetails?.loginId || 'User'}</span>
            <button className="sign-out-btn" onClick={signOut}>Sign Out</button>
          </div>
        </div>
      </header>
      
      <main className="main-content">
        <h2 className="products-title">Products</h2>
        <div className="product-list">
          {products.length === 0 ? (
            <p className="loading-text">Loading products...</p>
          ) : (
            products.map(product => (
              <div key={product.productId} className="product-card">
                <h3 className="product-name">{product.name}</h3>
                <p className="product-price">Price: ${product.price}</p>
                <button className="buy-btn" onClick={() => placeOrder(product.productId)}>
                  Buy Now
                </button>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  )
}

// This configures the Authenticator
export default withAuthenticator(App, {
  socialProviders: [],
  loginMechanisms: ['email'] // Use email as the login field
});