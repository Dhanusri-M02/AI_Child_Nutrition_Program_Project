

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getUser, logout, getUserName } from "../utils/auth";
import "../styles/Dashboard.css";

function ParentDashboard() {
  const user = getUser();
  const navigate = useNavigate();
  
  const [children, setChildren] = useState([]);
  const [selectedChild, setSelectedChild] = useState(null);
  const [sex, setSex] = useState("");
  const [age, setAge] = useState("");
  const [weight, setWeight] = useState("");
  const [height, setHeight] = useState("");
  const [childName, setChildName] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [advice, setAdvice] = useState("");
  const [healthRecords, setHealthRecords] = useState([]);
  const [showAddChild, setShowAddChild] = useState(false);
  const [error, setError] = useState("");

  // Load children on mount
  useEffect(() => {
    if (user && user.user_id) {
      loadChildren();
    }
  }, [user]);

  const loadChildren = async () => {
    try {
      console.log("Loading children for user_id:", user.user_id);
      const res = await fetch(`http://127.0.0.1:5000/children?parent_id=${user.user_id}`);
      console.log("Response status:", res.status);
      
      if (res.ok) {
        const data = await res.json();
        console.log("Children data:", data);
        setChildren(data);
      } else {
        const errData = await res.json();
        console.error("Error loading children:", errData);
        setError(errData.error || "Failed to load children");
      }
    } catch (error) {
      console.error("Error loading children:", error);
      setError("Cannot connect to server");
    }
  };

  const loadHealthRecords = async (childId) => {
    try {
      const res = await fetch(`http://127.0.0.1:5000/health-records?child_id=${childId}`);
      if (res.ok) {
        const data = await res.json();
        setHealthRecords(data);
      }
    } catch (error) {
      console.error("Error loading health records:", error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const handleAddChild = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const childData = {
        parent_id: user.user_id,
        name: childName,
        sex: sex,
        age: parseFloat(age),
        weight: parseFloat(weight),
        height: parseFloat(height)
      };
      
      console.log("Sending child data:", childData);

      const res = await fetch("http://127.0.0.1:5000/children", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(childData)
      });

      console.log("Add child response:", res.status);

      if (res.ok) {
        const data = await res.json();
        console.log("Child added:", data);
        alert("Child added successfully!");
        setShowAddChild(false);
        setChildName("");
        setSex("");
        setAge("");
        setWeight("");
        setHeight("");
        loadChildren();
      } else {
        const errData = await res.json();
        console.error("Error adding child:", errData);
        setError(errData.error || "Failed to add child");
        alert(errData.error || "Failed to add child");
      }
    } catch (error) {
      console.error("Error adding child:", error);
      setError("Cannot connect to server");
      alert("Error adding child");
    }

    setLoading(false);
  };

  const handleCheckNutrition = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus("");
    setAdvice("");
    setError("");

    try {
      // First get prediction
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sex, age, weight, height }),
      });

      const data = await response.json();
      setStatus(data.status);
      setAdvice(data.advice);

      // If child is selected, save health record
      if (selectedChild) {
        const recordRes = await fetch("http://127.0.0.1:5000/health-records", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            child_id: selectedChild.id,
            recorded_by: user.user_id,
            sex: sex,
            age: age,
            weight: weight,
            height: height,
            status: data.status,
            advice: data.advice
          })
        });
        
        if (recordRes.ok) {
          loadHealthRecords(selectedChild.id);
        }
      }

    } catch (error) {
      console.error("Error checking nutrition:", error);
      setStatus("Error");
      setAdvice("Unable to connect to server");
    }

    setLoading(false);
  };

  const handleSelectChild = (child) => {
    setSelectedChild(child);
    loadHealthRecords(child.id);
    setSex(child.sex);
    setAge(child.age.toString());
    setWeight(child.weight.toString());
    setHeight(child.height.toString());
  };

  if (!user) {
    return <div>Please login first</div>;
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h2>Parent Dashboard</h2>
        <div className="user-info">
          <span>Welcome, {getUserName() || user?.name}</span>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      {error && <div className="error-message">{error}</div>}

      <div className="dashboard-content">
        {/* Children List */}
        <div className="children-section">
          <div className="section-header">
            <h3>My Children</h3>
            <button onClick={() => setShowAddChild(!showAddChild)} className="add-btn">
              {showAddChild ? "Cancel" : "+ Add Child"}
            </button>
          </div>

          {showAddChild && (
            <div className="form-box">
              <h4>Add New Child</h4>
              <form onSubmit={handleAddChild}>
                <input 
                  type="text" 
                  placeholder="Child Name" 
                  value={childName} 
                  onChange={(e) => setChildName(e.target.value)} 
                  required 
                />
                <select value={sex} onChange={(e) => setSex(e.target.value)} required>
                  <option value="">Select Sex</option>
                  <option value="0">Female</option>
                  <option value="1">Male</option>
                </select>
                <input 
                  type="number" 
                  placeholder="Age (years)" 
                  value={age} 
                  onChange={(e) => setAge(e.target.value)} 
                  step="0.1"
                  required 
                />
                <input 
                  type="number" 
                  placeholder="Weight (kg)" 
                  value={weight} 
                  onChange={(e) => setWeight(e.target.value)} 
                  step="0.1"
                  required 
                />
                <input 
                  type="number" 
                  placeholder="Height (cm)" 
                  value={height} 
                  onChange={(e) => setHeight(e.target.value)} 
                  step="0.1"
                  required 
                />
                <button type="submit" disabled={loading}>
                  {loading ? "Adding..." : "Add Child"}
                </button>
              </form>
            </div>
          )}

          <div className="children-grid">
            {children.map((child) => (
              <div 
                key={child.id} 
                className={`child-card ${selectedChild?.id === child.id ? 'selected' : ''}`}
                onClick={() => handleSelectChild(child)}
              >
                <h4>{child.name}</h4>
                <p>Age: {child.age} years</p>
                <p>Sex: {child.sex === '1' ? 'Male' : 'Female'}</p>
                <p>Weight: {child.weight} kg</p>
                <p>Height: {child.height} cm</p>
              </div>
            ))}
            {children.length === 0 && !showAddChild && (
              <p className="empty-message">No children added yet. Click "Add Child" to get started.</p>
            )}
          </div>
        </div>

        {/* Nutrition Check Form */}
        {selectedChild && (
          <div className="form-box">
            <h3>Check Nutrition: {selectedChild.name}</h3>
            <form onSubmit={handleCheckNutrition}>
              <select value={sex} onChange={(e) => setSex(e.target.value)} required>
                <option value="">Select Sex</option>
                <option value="0">Female</option>
                <option value="1">Male</option>
              </select>
              <input 
                type="number" 
                placeholder="Age (years)" 
                value={age} 
                onChange={(e) => setAge(e.target.value)} 
                step="0.1"
                required 
              />
              <input 
                type="number" 
                placeholder="Weight (kg)" 
                value={weight} 
                onChange={(e) => setWeight(e.target.value)} 
                step="0.1"
                required 
              />
              <input 
                type="number" 
                placeholder="Height (cm)" 
                value={height} 
                onChange={(e) => setHeight(e.target.value)} 
                step="0.1"
                required 
              />
              <button type="submit" disabled={loading}>
                {loading ? "Checking..." : "Check Nutrition"}
              </button>
            </form>

            {status && (
              <div className="result-box">
                <p><strong>Status:</strong> {status}</p>
                <p><strong>Advice:</strong> {advice}</p>
              </div>
            )}
          </div>
        )}

        {/* Health Records History */}
        {healthRecords.length > 0 && (
          <div className="history-box">
            <h3>Health Records for {selectedChild?.name}</h3>
            <table>
              <thead>
                <tr>
                  <th>Age</th>
                  <th>Weight</th>
                  <th>Height</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {healthRecords.map((record) => (
                  <tr key={record.id}>
                    <td>{record.age}</td>
                    <td>{record.weight}</td>
                    <td>{record.height}</td>
                    <td>{record.status}</td>
                    <td>{new Date(record.recorded_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default ParentDashboard;


