import { useState } from "react";
import "./App.css";

function App() {
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
        body: JSON.stringify({
          sex: sex,
          age: age,
          weight: weight,
          height: height,
        }),
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
    <div className="container">
      <h2>Child Nutrition Monitor</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Sex (0 = Female, 1 = Male):</label>
          <input
            type="number"
            value={sex}
            onChange={(e) => setSex(e.target.value)}
          />
        </div>

        <div>
          <label>Age:</label>
          <input
            type="number"
            value={age}
            onChange={(e) => setAge(e.target.value)}
          />
        </div>

        <div>
          <label>Weight (kg):</label>
          <input
            type="number"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
          />
        </div>

        <div>
          <label>Height (cm):</label>
          <input
            type="number"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Checking..." : "Check Nutrition"}
        </button>
      </form>

      {loading && <div className="loader"></div>}

      {status && (
        <div className="result">
          <p><strong>Status:</strong> {status}</p>
          <p><strong>Advice:</strong> {advice}</p>
        </div>
      )}
    </div>
  );
}

export default App;
