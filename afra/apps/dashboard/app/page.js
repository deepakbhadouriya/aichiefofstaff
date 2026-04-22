"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const API_BASE_URL = "http://127.0.0.1:8000";

const PERSONA_CHOICES = [
  { id: "sme_owner", label: "SME AI Chief of Staff", summary: "The executive digital twin with custom communication and decision logic." },
  { id: "admin_user", label: "System Administrator", summary: "Full platform control and connector management." },
];

export default function LifeOSApp() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard"); // dashboard, inbox, crm, lab
  const [selectedProfile, setSelectedProfile] = useState("sme_owner");
  const [profile, setProfile] = useState(null);
  const [payments, setPayments] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [crm, setCrm] = useState({ contacts: [], recent_interactions: [], nudges: [] });
  const [workflowDetail, setWorkflowDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [agentThinking, setAgentThinking] = useState(false);
  const [statusMessage, setStatusMessage] = useState("System Standby");

  async function callApi(path, options = {}) {
    const { method = "GET", body, profileId = selectedProfile } = options;
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        "X-Profile-ID": profileId,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function syncAgent() {
    setLoading(true);
    setAgentThinking(true);
    try {
      const [profileData, paymentData, reviewData, crmData] = await Promise.all([
        callApi("/api/v1/profiles/me"),
        callApi("/api/v1/payments"),
        callApi("/api/v1/reviews"),
        callApi("/api/v1/crm/snapshot"),
      ]);
      setProfile(profileData);
      setPayments(paymentData);
      setReviews(reviewData);
      setCrm(crmData);
      setStatusMessage("Agent Synced");
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
      setTimeout(() => setAgentThinking(false), 1500);
    }
  }

  useEffect(() => {
    if (isLoggedIn) syncAgent();
  }, [isLoggedIn]);

  const handleLogin = (id) => {
    setSelectedProfile(id);
    setIsLoggedIn(true);
  };

  if (!isLoggedIn) {
    return (
      <div className="login-container">
        <div className="login-card">
          <div className="pulse-large"></div>
          <h1 style={{ marginBottom: '8px' }}>LifeOS</h1>
          <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>Executive Chief of Staff</p>
          <div className="persona-list" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {PERSONA_CHOICES.map(p => (
              <button key={p.id} className="lifeos-button btn-primary" onClick={() => handleLogin(p.id)}>
                Sign in as {p.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="lifeos-app">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: agentThinking ? 'var(--accent)' : '#333', boxShadow: agentThinking ? '0 0 10px var(--accent)' : 'none' }}></div>
          LifeOS
        </div>
        
        <nav className="nav-group">
          <button className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
            <span>📊</span> Dashboard
          </button>
          <button className={`nav-item ${activeTab === 'inbox' ? 'active' : ''}`} onClick={() => setActiveTab('inbox')}>
            <span>📬</span> Intelligence Inbox {reviews.length > 0 && <span style={{ marginLeft: 'auto', background: 'var(--gold)', color: '#000', padding: '2px 8px', borderRadius: '10px', fontSize: '0.7rem' }}>{reviews.length}</span>}
          </button>
          <button className={`nav-item ${activeTab === 'crm' ? 'active' : ''}`} onClick={() => setActiveTab('crm')}>
            <span>🤝</span> Relationship Pulse
          </button>
          <button className={`nav-item ${activeTab === 'lab' ? 'active' : ''}`} onClick={() => setActiveTab('lab')}>
            <span>🧠</span> Instruction Lab
          </button>
        </nav>

        <div style={{ marginTop: 'auto', padding: '16px', background: 'rgba(255,255,255,0.02)', borderRadius: '12px' }}>
          <p className="panel-title" style={{ fontSize: '0.65rem' }}>Agent Status</p>
          <p style={{ fontSize: '0.85rem', color: agentThinking ? 'var(--accent)' : 'var(--text-muted)' }}>
            {agentThinking ? "Thinking..." : "Listening..."}
          </p>
        </div>
      </aside>

      {/* Main Viewport */}
      <main className="main-viewport">
        <header style={{ marginBottom: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '1.8rem', fontWeight: '800' }}>{activeTab.toUpperCase()}</h1>
            <p style={{ color: 'var(--text-muted)' }}>Welcome back, {profile?.display_name || "Executive"}</p>
          </div>
          <button className="lifeos-button" style={{ width: 'auto', padding: '10px 20px', background: 'rgba(255,255,255,0.05)', color: 'white' }} onClick={() => setIsLoggedIn(false)}>
            Lock Console
          </button>
        </header>

        {activeTab === 'dashboard' && <DashboardView crm={crm} payments={payments} reviews={reviews} />}
        {activeTab === 'inbox' && <InboxView reviews={reviews} workflowDetail={workflowDetail} setWorkflowDetail={setWorkflowDetail} callApi={callApi} />}
        {activeTab === 'crm' && <CRMView crm={crm} />}
        {activeTab === 'lab' && <LabView profile={profile} setProfile={setProfile} callApi={callApi} setStatusMessage={setStatusMessage} />}
      </main>
    </div>
  );
}

function DashboardView({ crm, payments, reviews }) {
  return (
    <div className="dashboard-grid">
      <div className="glass-panel">
        <div className="panel-header">
          <p className="panel-title">Strategic Insight</p>
          <h3>Cash Runway</h3>
        </div>
        <h2 style={{ fontSize: '2.5rem', margin: '12px 0' }}>14 Months</h2>
        <p style={{ color: 'var(--text-muted)' }}>Calculated from {payments.length} recurring outflows and current reserves.</p>
      </div>

      <div className="glass-panel">
        <div className="panel-header">
          <p className="panel-title">Relationship Pulse</p>
          <h3>Active Stakeholders</h3>
        </div>
        <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
          {crm.contacts.map(c => (
            <div key={c.id} title={c.name} style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--bg-deep)', border: `2px solid ${c.status === 'Stale' ? '#ff3366' : 'var(--accent)'}`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {c.name[0]}
            </div>
          ))}
        </div>
      </div>

      <div className="glass-panel full-width">
        <div className="panel-header">
          <p className="panel-title">Recent Intelligence</p>
          <h3>Agent Activity Thread</h3>
        </div>
        <div className="feed">
          {payments.slice(0, 3).map(p => (
            <div className="feed-item" key={p.id}>
              <div className="feed-icon">₹</div>
              <div>
                <strong>Auto-paid {p.vendor_name}</strong>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Matched Gmail invoice to bank record.</p>
              </div>
              <div style={{ marginLeft: 'auto', fontWeight: '700' }}>₹{(p.amount_minor/100).toLocaleString()}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function InboxView({ reviews, workflowDetail, setWorkflowDetail, callApi }) {
  async function fetchDetail(id) {
    const data = await callApi(`/api/v1/workflows/${id}`);
    setWorkflowDetail(data);
  }

  return (
    <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
      <div className="glass-panel">
        <div className="panel-header">
          <p className="panel-title">Action Required</p>
          <h3>Intelligence Anomalies</h3>
        </div>
        <div className="feed">
          {reviews.map(r => (
            <div key={r.workflow_run_id} className={`feed-item ${workflowDetail?.id === r.workflow_run_id ? 'active' : ''}`} onClick={() => fetchDetail(r.workflow_run_id)} style={{ cursor: 'pointer', borderLeft: workflowDetail?.id === r.workflow_run_id ? '4px solid var(--gold)' : 'none' }}>
              <div className="feed-icon" style={{ color: 'var(--gold)' }}>⚠</div>
              <div>
                <strong>Review: {r.vendor_name}</strong>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Exceeds autopay threshold.</p>
              </div>
            </div>
          ))}
          {reviews.length === 0 && <p style={{ opacity: 0.3, padding: '20px' }}>Inbox zero. Agent is operating autonomously.</p>}
        </div>
      </div>

      <div className="glass-panel">
        <div className="panel-header">
          <p className="panel-title">Chain of Thought</p>
          <h3>Agentic Reasoning</h3>
        </div>
        {workflowDetail ? (
          <div className="detail-view">
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '12px', fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--accent)' }}>
              {workflowDetail.reasoning?.split(' | ').map((step, i) => (
                <div key={i} style={{ marginBottom: '8px' }}>
                  <span style={{ opacity: 0.4 }}>[{i+1}]</span> {step}
                </div>
              ))}
            </div>
            <div style={{ marginTop: '24px', display: 'flex', gap: '12px' }}>
              <button className="lifeos-button btn-primary">Approve Payment</button>
              <button className="lifeos-button" style={{ background: 'rgba(255,255,255,0.05)', color: 'white' }}>Reject & Draft Reply</button>
            </div>
          </div>
        ) : (
          <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.2 }}>
            Select an anomaly to inspect brain state.
          </div>
        )}
      </div>
    </div>
  );
}

function CRMView({ crm }) {
  return (
    <div className="glass-panel">
      <div className="panel-header">
        <p className="panel-title">Stakeholder Pulse</p>
        <h3>Executive Relationships</h3>
      </div>
      <div className="feed">
        {crm.contacts.map(c => (
          <div className="feed-item" key={c.id}>
            <div className="feed-icon">{c.name[0]}</div>
            <div>
              <strong>{c.name} ({c.company})</strong>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{c.summary}</p>
            </div>
            <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
              <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: c.status === 'Stale' ? '#ff3366' : 'var(--accent)' }}>{c.status}</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.5 }}>{new Date(c.last_interaction_at).toLocaleDateString()}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function LabView({ profile, setProfile, callApi, setStatusMessage }) {
  const [loading, setLoading] = useState(false);

  const handleUpdate = async () => {
    setLoading(true);
    try {
      await callApi("/api/v1/profiles/me/context", { 
        method: "POST", 
        body: { 
          communication_style: profile.communication_style,
          decision_preferences: profile.decision_preferences
        }
      });
      setStatusMessage("Brain Updated");
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ maxWidth: '800px' }}>
      <div className="panel-header">
        <p className="panel-title">Instruction Lab</p>
        <h3>Agent Brain Configuration</h3>
      </div>
      <div style={{ marginTop: '24px' }}>
        <div style={{ marginBottom: '24px' }}>
          <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Communication Context (Style of Speech)</label>
          <textarea 
            className="lifeos-input" 
            style={{ height: '120px', resize: 'vertical' }}
            value={profile?.communication_style || ""}
            onChange={(e) => setProfile({...profile, communication_style: e.target.value})}
          />
        </div>
        <div style={{ marginBottom: '32px' }}>
          <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Decision Context (Operational Choices)</label>
          <textarea 
            className="lifeos-input" 
            style={{ height: '120px', resize: 'vertical' }}
            value={profile?.decision_preferences || ""}
            onChange={(e) => setProfile({...profile, decision_preferences: e.target.value})}
          />
        </div>
        <button className="lifeos-button btn-primary" onClick={handleUpdate} disabled={loading}>
          {loading ? "Updating Agent Brain..." : "Deploy Instructions"}
        </button>
      </div>
    </div>
  );
}
