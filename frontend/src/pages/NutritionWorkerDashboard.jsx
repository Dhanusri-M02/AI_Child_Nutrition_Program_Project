
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getUser, logout, getUserName } from "../utils/auth";
import "../styles/Dashboard.css";

function NutritionWorkerDashboard() {
  const user = getUser();
  const navigate = useNavigate();
  
  const [allChildren, setAllChildren] = useState([]);
  const [parents, setParents] = useState([]);
  const [healthRecords, setHealthRecords] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedChild, setSelectedChild] = useState(null);
  const [showAddChild, setShowAddChild] = useState(false);
  const [error, setError] = useState("");
  
  // Form state
  const [sex, setSex] = useState("");
  const [age, setAge] = useState("");
  const [weight, setWeight] = useState("");
  const [height, setHeight] = useState("");
  const [status, setStatus] = useState("");
  const [advice, setAdvice] = useState("");
  
  // Add child form state
  const [childName, setChildName] = useState("");
  const [parentId, setParentId] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load all children
      const childrenRes = await fetch("http://127.0.0.1:5000/admin/children");
      if (childrenRes.ok) {
        const childrenData = await childrenRes.json();
        setAllChildren(childrenData);
      }

      // Load parents
      const parentsRes = await fetch("http://127.0.0.1:5000/parents");
      if (parentsRes.ok) {
        const parentsData = await parentsRes.json();
        setParents(parentsData);
      }

      // Load stats
      const statsRes = await fetch("http://127.0.0.1:5000/admin/stats");
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
    } catch (error) {
      console.error("Error loading data:", error);
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
      const res = await fetch("http://127.0.0.1:5000/children", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          parent_id: parseInt(parentId),
          name: childName,
          sex: sex,
          age: parseFloat(age),
          weight: parseFloat(weight),
          height: parseFloat(height)
        })
      });

      if (res.ok) {
        const data = await res.json();
        alert("Child added successfully!");
        setShowAddChild(false);
        setChildName("");
        setParentId("");
        setSex("");
        setAge("");
        setWeight("");
        setHeight("");
        loadData();
      } else {
        const errData = await res.json();
        setError(errData.error || "Failed to add child");
        alert(errData.error || "Failed to add child");
      }
    } catch (error) {
      console.error("Error adding child:", error);
      setError("Cannot connect to server");
    }

    setLoading(false);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus("");
    setAdvice("");

    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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

  const handleSaveRecord = async () => {
    if (!selectedChild || !status) return;

    try {
      await fetch("http://127.0.0.1:5000/health-records", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          child_id: selectedChild.id,
          recorded_by: user.user_id,
          sex, age, weight, height,
          status: status,
          advice: advice
        })
      });
      alert("Health record saved!");
      loadData();
    } catch (error) {
      alert("Error saving record");
    }
  };

  const handleSelectChild = (child) => {
    setSelectedChild(child);
    setSex(child.sex ? child.sex.toString() : "");
    setAge(child.age ? child.age.toString() : "");
    setWeight(child.weight ? child.weight.toString() : "");
    setHeight(child.height ? child.height.toString() : "");
    setStatus("");
    setAdvice("");
  };

  const handleDeleteChild = async (childId) => {
    if (!confirm("Are you sure you want to delete this child record?")) return;
    
    try {
      const res = await fetch(`http://127.0.0.1:5000/children/${childId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        alert("Child deleted!");
        loadData();
      }
    } catch (error) {
      alert("Error deleting child");
    }
  };

  // Calculate stats from children data
  const totalChildren = allChildren.length;
  const childStats = stats.health_stats || [];
  const normalCount = childStats.find(s => s.status === 'Normal')?.count || 0;
  const underweightCount = childStats.filter(s => s.status === 'Underweight').reduce((a, b) => a + b.count, 0);
  const overweightCount = childStats.filter(s => s.status === 'Overweight').reduce((a, b) => a + b.count, 0);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h2>Nutrition Worker Dashboard</h2>
        <div className="user-info">
          <span>Welcome, {getUserName() || user?.name}</span>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      {error && <div className="error-message">{error}</div>}

      <div className="dashboard-content">
        {/* Statistics Cards */}
        <div className="stats-container">
          <div className="stat-card">
            <h3>Total Children</h3>
            <p className="stat-number">{totalChildren}</p>
          </div>
          <div className="stat-card normal">
            <h3>Normal</h3>
            <p className="stat-number">{normalCount}</p>
          </div>
          <div className="stat-card warning">
            <h3>Underweight</h3>
            <p className="stat-number">{underweightCount}</p>
          </div>
          <div className="stat-card danger">
            <h3>Overweight</h3>
            <p className="stat-number">{overweightCount}</p>
          </div>
        </div>

        {/* Forms Section */}
        <div className="worker-forms-section">
          {/* Add Child Form */}
          <div className="form-box">
            <div className="section-header">
              <h3>Add New Child</h3>
              <button onClick={() => setShowAddChild(!showAddChild)} className="add-btn">
                {showAddChild ? "Cancel" : "+ Add Child"}
              </button>
            </div>
            
            {showAddChild && (
              <form onSubmit={handleAddChild}>
                <input 
                  type="text" 
                  placeholder="Child Name" 
                  value={childName}
                  onChange={(e) => setChildName(e.target.value)}
                  required 
                />
                <select 
                  value={parentId} 
                  onChange={(e) => setParentId(e.target.value)}
                  required
                >
                  <option value="">Select Parent</option>
                  {parents.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.email})
                    </option>
                  ))}
                </select>
                <select value={sex} onChange={(e) => setSex(e.target.value)} required>
                  <option value="">Select Sex</option>
                  <option value="0">Female</option>
                  <option value="1">Male</option>
                </select>
                <input type="number" placeholder="Age (years)" value={age} 
                  onChange={(e) => setAge(e.target.value)} step="0.1" required />
                <input type="number" placeholder="Weight (kg)" value={weight} 
                  onChange={(e) => setWeight(e.target.value)} step="0.1" required />
                <input type="number" placeholder="Height (cm)" value={height} 
                  onChange={(e) => setHeight(e.target.value)} step="0.1" required />
                <button type="submit" disabled={loading}>
                  {loading ? "Adding..." : "Add Child"}
                </button>
              </form>
            )}
            {!showAddChild && (
              <p className="form-hint">Click the button above to add a new child to the system.</p>
            )}
          </div>

          {/* Analysis Form */}
          <div className="form-box">
            <h3>Analyze Child Nutrition</h3>
            <form onSubmit={handleAnalyze}>
              <select value={sex} onChange={(e) => setSex(e.target.value)} required>
                <option value="">Select Sex</option>
                <option value="0">Female</option>
                <option value="1">Male</option>
              </select>
              <input type="number" placeholder="Age (years)" value={age} 
                onChange={(e) => setAge(e.target.value)} required />
              <input type="number" placeholder="Weight (kg)" value={weight} 
                onChange={(e) => setWeight(e.target.value)} required />
              <input type="number" placeholder="Height (cm)" value={height} 
                onChange={(e) => setHeight(e.target.value)} required />
              <button type="submit" disabled={loading}>
                {loading ? "Analyzing..." : "Analyze"}
              </button>
            </form>

            {status && (
              <div className="result-box">
                <p><strong>Status:</strong> {status}</p>
                <p><strong>Advice:</strong> {advice}</p>
                {selectedChild && (
                  <button onClick={handleSaveRecord} className="save-btn">
                    Save Record
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Children List */}
        <div className="children-list">
          <h3>All Children ({totalChildren})</h3>
          {allChildren.length === 0 ? (
            <p className="empty-message">No children records found.</p>
          ) : (
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Parent</th>
                    <th>Age</th>
                    <th>Sex</th>
                    <th>Weight</th>
                    <th>Height</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {allChildren.map((child) => (
                    <tr key={child.id}>
                      <td>{child.name}</td>
                      <td>{child.parent_name || 'N/A'}</td>
                      <td>{child.age}</td>
                      <td>{child.sex === '1' ? 'Male' : 'Female'}</td>
                      <td>{child.weight}</td>
                      <td>{child.height}</td>
                      <td>
                        <button onClick={() => handleSelectChild(child)} className="edit-btn">Select</button>
                        <button onClick={() => handleDeleteChild(child.id)} className="delete-btn">Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default NutritionWorkerDashboard;

