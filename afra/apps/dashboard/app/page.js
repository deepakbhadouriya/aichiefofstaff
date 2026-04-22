"use client";

import { useState, useEffect } from "react";

const API_BASE_URL = "http://127.0.0.1:8000";

export default function FintechDashboard() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard"); // dashboard, review, transactions, rules
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  
  // App State
  const [profile, setProfile] = useState(null);
  const [payments, setPayments] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [statusMessage, setStatusMessage] = useState("AI Agent: System Ready");

  // Rule Builder State
  const [ruleInput, setRuleInput] = useState("");
  const [parsedRule, setParsedRule] = useState(null);

  async function callApi(path, options = {}) {
    const { method = "GET", body, profileId = "sme_owner" } = options;
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

  const syncData = async () => {
    try {
      const [p, pay, rev] = await Promise.all([
        callApi("/api/v1/profiles/me"),
        callApi("/api/v1/payments"),
        callApi("/api/v1/reviews"),
      ]);
      setProfile(p);
      setPayments(pay);
      setReviews(rev);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (isLoggedIn) syncData();
  }, [isLoggedIn]);

  const handleRuleInput = (val) => {
    setRuleInput(val);
    // Simple mock parsing logic for demo
    if (val.toLowerCase().includes("electricity") && val.toLowerCase().includes("10000")) {
      setParsedRule({ category: "Electricity", threshold: "₹10,000", action: "Auto-pay" });
    } else {
      setParsedRule(null);
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="login-screen">
        <div className="login-box">
          <div className="sidebar-brand" style={{ justifyContent: 'center', marginBottom: '40px' }}>
            <span>Afra</span>
          </div>
          <h2 style={{ textAlign: 'center', marginBottom: '8px' }}>Sign in</h2>
          <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '32px' }}>Enter your email to receive an OTP</p>
          
          <input className="input-field" type="email" placeholder="name@company.com" style={{ marginBottom: '16px' }} />
          <button className="btn btn-primary" style={{ width: '100%', marginBottom: '16px' }} onClick={() => setIsLoggedIn(true)}>
            Send OTP
          </button>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: '24px 0' }}>
            <div style={{ height: '1px', flex: 1, background: 'var(--border)' }}></div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>OR</span>
            <div style={{ height: '1px', flex: 1, background: 'var(--border)' }}></div>
          </div>
          
          <button className="btn btn-outline" style={{ width: '100%' }} onClick={() => setIsLoggedIn(true)}>
            Login as Demo User
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div style={{ width: '24px', height: '24px', background: 'var(--primary)', borderRadius: '6px' }}></div>
          Afra
        </div>
        
        <nav style={{ display: 'flex', flex_direction: 'column', gap: '4px' }}>
          <button className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => { setActiveTab('dashboard'); setSelectedWorkflow(null); }}>
            Dashboard
          </button>
          <button className={`nav-link ${activeTab === 'review' ? 'active' : ''}`} onClick={() => { setActiveTab('review'); setSelectedWorkflow(null); }}>
            Review Queue
          </button>
          <button className={`nav-link ${activeTab === 'transactions' ? 'active' : ''}`} onClick={() => { setActiveTab('transactions'); setSelectedWorkflow(null); }}>
            Transactions
          </button>
          <button className={`nav-link ${activeTab === 'rules' ? 'active' : ''}`} onClick={() => { setActiveTab('rules'); setSelectedWorkflow(null); }}>
            Rule Builder
          </button>
        </nav>

        <div style={{ marginTop: 'auto', padding: '12px' }}>
          <div className="ai-status">
            <div className="pulse"></div>
            {statusMessage}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {selectedWorkflow ? (
          <TransactionDetailView workflow={selectedWorkflow} onBack={() => setSelectedWorkflow(null)} />
        ) : (
          <>
            {activeTab === 'dashboard' && <DashboardView payments={payments} reviews={reviews} onAction={() => setActiveTab('rules')} onDetail={setSelectedWorkflow} callApi={callApi} />}
            {activeTab === 'review' && <ReviewQueueView reviews={reviews} onDetail={setSelectedWorkflow} callApi={callApi} sync={syncData} />}
            {activeTab === 'transactions' && <TransactionsView payments={payments} onDetail={setSelectedWorkflow} callApi={callApi} />}
            {activeTab === 'rules' && <RuleBuilderView input={ruleInput} onInput={handleRuleInput} parsed={parsedRule} />}
          </>
        )}
      </main>
    </div>
  );
}

function DashboardView({ payments, reviews, onAction, onDetail, callApi }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <h2>Dashboard</h2>
        <button className="btn btn-primary" onClick={onAction}>Create Rule</button>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <p className="metric-label">Total Bills This Month</p>
          <p className="metric-value">{payments.length + reviews.length}</p>
        </div>
        <div className="metric-card">
          <p className="metric-label">Auto-paid</p>
          <p className="metric-value" style={{ color: 'var(--success)' }}>{payments.length}</p>
        </div>
        <div className="metric-card">
          <p className="metric-label">Pending Review</p>
          <p className="metric-value" style={{ color: 'var(--warning)' }}>{reviews.length}</p>
        </div>
        <div className="metric-card">
          <p className="metric-label">Alerts</p>
          <p className="metric-value" style={{ color: 'var(--danger)' }}>2</p>
        </div>
      </div>

      <div className="card">
        <h3>Recent Transactions</h3>
        <table className="data-table" style={{ marginTop: '20px' }}>
          <thead>
            <tr>
              <th>Vendor</th>
              <th>Date</th>
              <th>Amount</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {payments.slice(0, 5).map(p => (
              <tr key={p.id}>
                <td style={{ fontWeight: 600 }}>{p.vendor_name}</td>
                <td>{new Date(p.created_at).toLocaleDateString()}</td>
                <td>₹{(p.amount_minor/100).toLocaleString()}</td>
                <td><span className="badge badge-success">Auto-paid</span></td>
                <td><button className="btn btn-outline" style={{ padding: '6px 12px' }} onClick={async () => {
                  const detail = await callApi(`/api/v1/workflows/wf-sme_owner-${p.vendor_name.toLowerCase().replace(' ', '-')}`);
                  onDetail(detail);
                }}>View</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function RuleBuilderView({ input, onInput, parsed }) {
  return (
    <div style={{ maxWidth: '600px' }}>
      <h2 style={{ marginBottom: '32px' }}>Create New Rule</h2>
      <div className="card">
        <p className="metric-label" style={{ marginBottom: '12px' }}>Natural Language Input</p>
        <textarea 
          className="input-field" 
          placeholder="e.g. Auto-pay electricity bills under ₹10,000" 
          style={{ height: '100px', resize: 'none' }}
          value={input}
          onChange={(e) => onInput(e.target.value)}
        />
        
        {parsed && (
          <div style={{ marginTop: '32px', padding: '20px', background: '#f8fafc', borderRadius: '12px', border: '1px solid var(--border)' }}>
            <p className="metric-label" style={{ marginBottom: '16px' }}>AI Parsed Logic</p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Category</p>
                <p style={{ fontWeight: 600 }}>{parsed.category}</p>
              </div>
              <div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Threshold</p>
                <p style={{ fontWeight: 600 }}>{parsed.threshold}</p>
              </div>
              <div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Action</p>
                <p style={{ fontWeight: 600 }}>{parsed.action}</p>
              </div>
            </div>
          </div>
        )}

        <div style={{ marginTop: '32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <p style={{ fontWeight: 600 }}>Require approval above threshold</p>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Flag bills exceeding the limit for manual review.</p>
          </div>
          <div style={{ width: '40px', height: '20px', background: 'var(--primary)', borderRadius: '20px', position: 'relative' }}>
            <div style={{ width: '16px', height: '16px', background: 'white', borderRadius: '50%', position: 'absolute', right: '2px', top: '2px' }}></div>
          </div>
        </div>

        <button className="btn btn-primary" style={{ width: '100%', marginTop: '32px' }}>Save Rule</button>
      </div>
    </div>
  );
}

function ReviewQueueView({ reviews, onDetail, callApi, sync }) {
  return (
    <div>
      <h2 style={{ marginBottom: '32px' }}>Review Queue</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '24px' }}>
        {reviews.map(r => (
          <div className="card" key={r.workflow_run_id}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '20px' }}>
              <div>
                <h4 style={{ fontSize: '1.1rem' }}>{r.vendor_name}</h4>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Biller Ref: {r.workflow_run_id.split('-').pop()}</p>
              </div>
              <p style={{ fontSize: '1.25rem', fontWeight: 700 }}>₹{(r.amount_minor/100).toLocaleString()}</p>
            </div>
            
            <div style={{ padding: '12px', background: '#fffbeb', borderRadius: '8px', border: '1px solid #fef3c7', marginBottom: '24px' }}>
              <p style={{ fontSize: '0.85rem', color: '#92400e' }}><strong>Reason:</strong> {r.reason}</p>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button className="btn btn-primary" style={{ flex: 1 }}>Approve</button>
              <button className="btn btn-outline" style={{ flex: 1 }}>Reject</button>
              <button className="btn btn-outline" style={{ padding: '10px' }} onClick={async () => {
                const detail = await callApi(`/api/v1/workflows/${r.workflow_run_id}`);
                onDetail(detail);
              }}>Details</button>
            </div>
          </div>
        ))}
        {reviews.length === 0 && <p style={{ color: 'var(--text-muted)' }}>Nothing to review. All systems nominal.</p>}
      </div>
    </div>
  );
}

function TransactionsView({ payments, onDetail, callApi }) {
  return (
    <div>
      <h2 style={{ marginBottom: '32px' }}>All Transactions</h2>
      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Vendor</th>
              <th>Date</th>
              <th>Amount</th>
              <th>Method</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {payments.map(p => (
              <tr key={p.id}>
                <td style={{ fontWeight: 600 }}>{p.vendor_name}</td>
                <td>{new Date(p.created_at).toLocaleDateString()}</td>
                <td>₹{(p.amount_minor/100).toLocaleString()}</td>
                <td><span style={{ color: 'var(--text-muted)' }}>Bank Transfer</span></td>
                <td><span className="badge badge-success">Success</span></td>
                <td><button className="btn btn-outline" style={{ padding: '6px 12px' }} onClick={async () => {
                  const detail = await callApi(`/api/v1/workflows/wf-sme_owner-${p.vendor_name.toLowerCase().replace(' ', '-')}`);
                  onDetail(detail);
                }}>View</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function TransactionDetailView({ workflow, onBack }) {
  const isAutoPay = workflow.decision === 'approved_for_autopay';
  const isPending = workflow.current_state === 'pending_human_review';
  
  return (
    <div style={{ maxWidth: '1000px' }}>
      <button className="nav-link" onClick={onBack} style={{ marginBottom: '24px', width: 'auto' }}>← Back to Dashboard</button>
      
      <div className="card" style={{ marginBottom: '32px' }}>
        <p className="metric-label" style={{ marginBottom: '24px' }}>Agentic Decision Path</p>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '20px', background: '#f8fafc', borderRadius: '12px' }}>
          <svg width="600" height="240" viewBox="0 0 600 240">
            {/* Core Nodes */}
            <FlowNode x={300} y={40} label="Fetch Bill" active={true} />
            <FlowNode x={300} y={100} label="Validate & Decision Gate" active={true} />
            
            {/* Branches */}
            <path d="M 300 120 L 150 160" stroke={isAutoPay ? "var(--primary)" : "#e3e8ee"} strokeWidth="2" fill="none" />
            <path d="M 300 120 L 450 160" stroke={!isAutoPay ? "var(--warning)" : "#e3e8ee"} strokeWidth="2" fill="none" />
            
            <FlowNode x={150} y={180} label="Auto Pay" active={isAutoPay} type="auto" />
            <FlowNode x={450} y={180} label="Human Review" active={!isAutoPay} type="hitl" />
            
            {/* Final Path */}
            <path d="M 150 200 L 300 240" stroke={isAutoPay ? "var(--primary)" : "#e3e8ee"} strokeWidth="2" fill="none" />
            <path d="M 450 200 L 300 240" stroke={!isAutoPay ? "var(--primary)" : "#e3e8ee"} strokeWidth="2" fill="none" />
            
            <circle cx="300" cy="240" r="6" fill={workflow.current_state === 'ledger_updated' ? "var(--success)" : "#e3e8ee"} />
            <text x="315" y="245" fontSize="10" fill="var(--text-muted)">Audit + Notify</text>
          </svg>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px' }}>
        <div>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
              <div>
                <h2>{workflow.request.vendor_name}</h2>
                <p style={{ color: 'var(--text-muted)' }}>Payment for {workflow.request.category}</p>
              </div>
              <h2 style={{ fontSize: '2rem' }}>₹{(workflow.amount_minor/100).toLocaleString()}</h2>
            </div>
            
            <div style={{ background: '#f0f9ff', padding: '16px', borderRadius: '12px', border: '1px solid #bae6fd', marginBottom: '24px' }}>
              <p className="metric-label" style={{ color: 'var(--primary)', marginBottom: '8px' }}>AI Context</p>
              <p style={{ fontSize: '0.85rem', lineHeight: '1.5' }}>{workflow.reasoning?.split(' | ').pop() || "Analyzing context..."}</p>
            </div>
            
            <h3>Intelligence Evidence</h3>
            <div style={{ display: 'flex', gap: '16px', marginTop: '16px' }}>
              {workflow.evidence.map(e => (
                <div key={e.source_id} style={{ width: '100px', height: '140px', background: 'white', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                  <span style={{ fontSize: '1.5rem' }}>📄</span>
                  <p style={{ fontSize: '0.6rem', marginTop: '8px', textTransform: 'uppercase' }}>{e.source_type}</p>
                  <p style={{ fontSize: '0.7rem', color: 'var(--success)', fontWeight: 700 }}>{Math.round(e.confidence * 100)}%</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <p className="metric-label" style={{ marginBottom: '16px' }}>Audit Details</p>
          <div style={{ fontSize: '0.85rem' }}>
            <p style={{ marginBottom: '12px' }}><span style={{ color: 'var(--text-muted)' }}>Workflow:</span> {workflow.id}</p>
            <p style={{ marginBottom: '12px' }}><span style={{ color: 'var(--text-muted)' }}>Status:</span> <strong>{workflow.current_state}</strong></p>
            <p style={{ marginBottom: '12px' }}><span style={{ color: 'var(--text-muted)' }}>Request:</span> {workflow.x_request_id}</p>
          </div>
          {isPending && (
            <div style={{ marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button className="btn btn-primary">Approve & Execute</button>
              <button className="btn btn-outline">Reject Payment</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function FlowNode({ x, y, label, active, type }) {
  const color = type === 'auto' ? 'var(--primary)' : type === 'hitl' ? 'var(--warning)' : 'var(--text-main)';
  return (
    <g>
      <rect x={x - 80} y={y - 20} width={160} height={40} rx="8" fill="white" stroke={active ? color : "#e3e8ee"} strokeWidth="2" style={{ filter: active ? 'drop-shadow(0 0 4px rgba(0,0,0,0.05))' : 'none' }} />
      <text x={x} y={y + 5} textAnchor="middle" fontSize="11" fontWeight={active ? "600" : "400"} fill={active ? "var(--text-main)" : "var(--text-muted)"}>{label}</text>
      {active && <circle cx={x - 70} cy={y} r="4" fill={color} />}
    </g>
  );
}

function TimelineItem({ label, date, active }) {
  return (
    <div className="timeline-item">
      <div className={`timeline-dot ${active ? 'active' : ''}`}></div>
      <div className="timeline-line"></div>
      <div style={{ flex: 1 }}>
        <p style={{ fontWeight: 600, fontSize: '0.9rem', color: active ? 'var(--text-main)' : 'var(--text-muted)' }}>{label}</p>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{active ? new Date(date).toLocaleString() : 'Pending'}</p>
      </div>
    </div>
  );
}
