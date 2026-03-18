import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { setAuthData, getRoleBasedRoute, getAuthHeaders } from "../utils/auth";
import "../styles/Login.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [otpId, setOtpId] = useState(null);
  const [isAdminLogin, setIsAdminLogin] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:5000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (res.ok) {
        if (data.otp_id) {
          // Admin OTP flow
          setOtpId(data.otp_id);
          setIsAdminLogin(true);
          alert("OTP sent to your email. Enter OTP:");
        } else {
          // Non-admin success
          setAuthData(data.token, {
            user_id: data.user_id,
            name: data.name,
            email,
            role: data.role
          });
          const redirectPath = getRoleBasedRoute(data.role);
          navigate(redirectPath);
        }
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert("Server not reachable");
      console.error(error);
    }
    setLoading(false);
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:5000/auth/admin/verify-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ otp_id: otpId, otp }),
      });

      const data = await res.json();

      if (res.ok) {
        setAuthData(data.token, {
          user_id: data.user_id,
          name: data.name,
          email,
          role: data.role
        });
        navigate("/dashboard/admin");
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert("Server not reachable");
      console.error(error);
    }
    setLoading(false);
  };

  return (
    <div className="login-container">
      <h2>{isAdminLogin ? "Admin OTP Verification" : "Login"}</h2>

      {!isAdminLogin ? (
        <form onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            required
            onChange={(e) => setEmail(e.target.value)}
            value={email}
          />

          <input
            type="password"
            placeholder="Password"
            required
            onChange={(e) => setPassword(e.target.value)}
            value={password}
          />

          <button type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOtp}>
          <input
            type="text"
            placeholder="Enter 6-digit OTP"
            required
            onChange={(e) => setOtp(e.target.value)}
            value={otp}
            maxLength="6"
          />

          <button type="submit" disabled={loading}>
            {loading ? "Verifying..." : "Verify OTP"}
          </button>
        </form>
      )}

      {!isAdminLogin && (
        <p>
          Don't have an account? <Link to="/signup">Signup</Link>
        </p>
      )}
    </div>
  );
}

export default Login;

