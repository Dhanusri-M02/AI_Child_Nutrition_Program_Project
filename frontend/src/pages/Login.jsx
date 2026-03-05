import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { setUser, getRoleBasedRoute } from "../utils/auth";
import "../styles/Login.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (res.ok) {
        // Store user info in localStorage
        setUser({
          user_id: data.user_id,
          name: data.name,
          email: email,
          role: data.role
        });
        
        // Route to appropriate dashboard based on role
        const redirectPath = getRoleBasedRoute(data.role);
        navigate(redirectPath);
      } else {
        alert(data.message);
      }

    } catch (error) {
      alert("Server not reachable");
      console.error(error);
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>

      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          required
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          required
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit">Login</button>
      </form>

      <p>
        Don't have an account? <Link to="/signup">Signup</Link>
      </p>
    </div>
  );
}

export default Login;

