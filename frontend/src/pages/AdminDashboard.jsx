

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getUser, logout, getUserName } from "../utils/auth";
import "../styles/Dashboard.css";

function AdminDashboard() {
  const user = getUser();
  const navigate = useNavigate();
  
  const [users, setUsers] = useState([]);
  const [children, setChildren] = useState([]);
  const [healthRecords, setHealthRecords] = useState([]);
  const [stats, setStats] = useState({});
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load all users
      const usersRes = await fetch("http://127.0.0.1:5000/admin/users");
      if (usersRes.ok) {
        const usersData = await usersRes.json();
        setUsers(usersData);
      }

      // Load all children
      const childrenRes = await fetch("http://127.0.0.1:5000/admin/children");
      if (childrenRes.ok) {
        const childrenData = await childrenRes.json();
        setChildren(childrenData);
      }

      // Load all health records
      const recordsRes = await fetch("http://127.0.0.1:5000/admin/health-records");
      if (recordsRes.ok) {
        const recordsData = await recordsRes.json();
        setHealthRecords(recordsData);
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
    setLoading(false);
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const handleDeleteUser = async (userId) => {
    if (!confirm("Are you sure you want to delete this user?")) return;
    
    try {
      const res = await fetch(`http://127.0.0.1:5000/admin/users/${userId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        alert("User deleted!");
        loadData();
      }
    } catch (error) {
      alert("Error deleting user");
    }
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

  // Statistics from API
  const userStats = stats.user_stats || [];
  const totalUsers = users.length;
  const parentCount = userStats.find(u => u.role === 'parent')?.count || 0;
  const workerCount = userStats.find(u => u.role === 'nutrition_worker')?.count || 0;
  const adminCount = userStats.find(u => u.role === 'admin')?.count || 0;
  
  const totalChildren = children.length;
  const healthStats = stats.health_stats || [];
  const normalCount = healthStats.find(s => s.status === 'Normal')?.count || 0;
  const underweightCount = healthStats.filter(s => s.status === 'Underweight').reduce((a, b) => a + b.count, 0);
  const overweightCount = healthStats.filter(s => s.status === 'Overweight').reduce((a, b) => a + b.count, 0);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h2>Admin Dashboard</h2>
        <div className="user-info">
          <span>Welcome, {getUserName() || user?.name} (Admin)</span>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="dashboard-content">
        {/* Navigation Tabs */}
        <div className="admin-tabs">
          <button 
            className={activeTab === "overview" ? "active" : ""} 
            onClick={() => setActiveTab("overview")}
          >
            Overview
          </button>
          <button 
            className={activeTab === "users" ? "active" : ""} 
            onClick={() => setActiveTab("users")}
          >
            Manage Users
          </button>
          <button 
            className={activeTab === "children" ? "active" : ""} 
            onClick={() => setActiveTab("children")}
          >
            Manage Children Data
          </button>
          <button 
            className={activeTab === "records" ? "active" : ""} 
            onClick={() => setActiveTab("records")}
          >
            Health Records
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="overview-section">
            <h3>System Overview</h3>
            {loading ? (
              <p>Loading...</p>
            ) : (
              <>
                <div className="stats-container">
                  <div className="stat-card">
                    <h3>Total Users</h3>
                    <p className="stat-number">{totalUsers}</p>
                  </div>
                  <div className="stat-card">
                    <h3>Parents</h3>
                    <p className="stat-number">{parentCount}</p>
                  </div>
                  <div className="stat-card">
                    <h3>Nutrition Workers</h3>
                    <p className="stat-number">{workerCount}</p>
                  </div>
                  <div className="stat-card">
                    <h3>Admins</h3>
                    <p className="stat-number">{adminCount}</p>
                  </div>
                </div>

                <div className="stats-container">
                  <div className="stat-card">
                    <h3>Total Children Records</h3>
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
              </>
            )}
          </div>
        )}

        {/* Users Tab */}
        {activeTab === "users" && (
          <div className="users-section">
            <h3>User Management</h3>
            {loading ? (
              <p>Loading...</p>
            ) : users.length === 0 ? (
              <p className="empty-message">No users registered yet.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Created At</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id}>
                      <td>{u.id}</td>
                      <td>{u.name}</td>
                      <td>{u.email}</td>
                      <td className={`role-${u.role}`}>{u.role.replace('_', ' ')}</td>
                      <td>{new Date(u.created_at).toLocaleDateString()}</td>
                      <td>
                        <button onClick={() => handleDeleteUser(u.id)} className="delete-btn">
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* Children Data Tab */}
        {activeTab === "children" && (
          <div className="children-section">
            <h3>Children Data Management</h3>
            {loading ? (
              <p>Loading...</p>
            ) : children.length === 0 ? (
              <p className="empty-message">No children records found.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
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
                  {children.map((child) => (
                    <tr key={child.id}>
                      <td>{child.id}</td>
                      <td>{child.name}</td>
                      <td>{child.parent_name}</td>
                      <td>{child.age}</td>
                      <td>{child.sex === '1' ? 'Male' : 'Female'}</td>
                      <td>{child.weight}</td>
                      <td>{child.height}</td>
                      <td>
                        <button onClick={() => handleDeleteChild(child.id)} className="delete-btn">
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* Health Records Tab */}
        {activeTab === "records" && (
          <div className="records-section">
            <h3>All Health Records</h3>
            {loading ? (
              <p>Loading...</p>
            ) : healthRecords.length === 0 ? (
              <p className="empty-message">No health records found.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Child</th>
                    <th>Recorded By</th>
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
                      <td>{record.child_name}</td>
                      <td>{record.recorded_by_name} ({record.recorded_by_role})</td>
                      <td>{record.age}</td>
                      <td>{record.weight}</td>
                      <td>{record.height}</td>
                      <td className={`status-${record.status?.toLowerCase()}`}>{record.status}</td>
                      <td>{new Date(record.recorded_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminDashboard;


