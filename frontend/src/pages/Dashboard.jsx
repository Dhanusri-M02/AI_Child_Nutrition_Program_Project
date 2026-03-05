import { useState } from "react";
import "../styles/Dashboard.css";

function Dashboard() {
  const [sex, setSex] = useState("");
  const [age, setAge] = useState("");
  const [weight, setWeight] = useState("");
  const [height, setHeight] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [advice, setAdvice] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus("");
    setAdvice("");

    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sex, age, weight, height }),
      });

      const data = await response.json();
      setStatus(data.status);
      setAdvice(data.advice);

    } catch (error) {
      setStatus("Error");
      setAdvice("Unable to connect to server");
    }

    setLoading(false);
  };

  return (
    <div className="dashboard-container">
      <h2>Child Nutrition Monitor</h2>

      <form className="form-box" onSubmit={handleSubmit}>
        <input
          type="number"
          placeholder="Sex (0=Female, 1=Male)"
          value={sex}
          onChange={(e) => setSex(e.target.value)}
          required
        />

        <input
          type="number"
          placeholder="Age"
          value={age}
          onChange={(e) => setAge(e.target.value)}
          required
        />

        <input
          type="number"
          placeholder="Weight"
          value={weight}
          onChange={(e) => setWeight(e.target.value)}
          required
        />

        <input
          type="number"
          placeholder="Height"
          value={height}
          onChange={(e) => setHeight(e.target.value)}
          required
        />

        <button type="submit" disabled={loading}>
          {loading ? "Checking..." : "Check Nutrition"}
        </button>
      </form>

      {status && (
        <div>
          <p><strong>Status:</strong> {status}</p>
          <p><strong>Advice:</strong> {advice}</p>
        </div>
      )}
    </div>
  );
}

export default Dashboard;