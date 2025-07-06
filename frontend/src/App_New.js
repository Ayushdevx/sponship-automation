import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const API = `${BACKEND_URL}/api`;

function App() {
  // Core state
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sponsors, setSponsors] = useState([]);
  const [participants, setParticipants] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [sponsorStats, setSponsorStats] = useState({ total: 0, sent: 0, failed: 0, pending: 0 });
  const [certificateStats, setCertificateStats] = useState({ total: 0, sent: 0, failed: 0, pending: 0 });
  const [uploadStatus, setUploadStatus] = useState('');
  const [sendingStatus, setSendingStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isSending, setIsSending] = useState(false);

  // 📧 EMAIL SCHEDULING STATE
  const [scheduledEmails, setScheduledEmails] = useState([]);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [scheduleForm, setScheduleForm] = useState({
    recipient_email: '',
    subject: '',
    content: '',
    schedule_date: '',
    schedule_time: '',
    template_type: 'sponsor',
    priority: 'normal',
    recurring: false
  });

  // 📁 DRAG & DROP STATE
  const [dragDropArea, setDragDropArea] = useState({
    isDragOver: false,
    uploadProgress: 0,
    isProcessing: false
  });
  const [showUploadPreview, setShowUploadPreview] = useState(false);
  const [uploadPreviewData, setUploadPreviewData] = useState(null);

  // 🎨 UI/UX STATE
  const [theme, setTheme] = useState('light');
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);

  // EFFECTS
  useEffect(() => {
    fetchInitialData();
    const interval = setInterval(() => {
      if (isSending) {
        fetchSponsorStats();
        fetchCertificateStats();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [isSending]);

  // FETCH FUNCTIONS
  const fetchInitialData = async () => {
    try {
      await Promise.all([
        fetchSponsors(),
        fetchParticipants(),
        fetchTemplates(),
        fetchSponsorStats(),
        fetchCertificateStats(),
        fetchScheduledEmails()
      ]);
    } catch (error) {
      console.error('Error fetching initial data:', error);
      addNotification('Error fetching data', 'error');
    }
  };

  const fetchSponsors = async () => {
    try {
      const response = await axios.get(`${API}/sponsors`);
      setSponsors(response.data);
    } catch (error) {
      console.error('Error fetching sponsors:', error);
    }
  };

  const fetchParticipants = async () => {
    try {
      const response = await axios.get(`${API}/participants`);
      setParticipants(response.data);
    } catch (error) {
      console.error('Error fetching participants:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await axios.get(`${API}/templates`);
      setTemplates(response.data);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const fetchSponsorStats = async () => {
    try {
      const response = await axios.get(`${API}/email-stats`);
      setSponsorStats(response.data);
    } catch (error) {
      console.error('Error fetching sponsor stats:', error);
    }
  };

  const fetchCertificateStats = async () => {
    try {
      const response = await axios.get(`${API}/certificate-stats`);
      setCertificateStats(response.data);
    } catch (error) {
      console.error('Error fetching certificate stats:', error);
    }
  };

  const fetchScheduledEmails = async () => {
    try {
      const response = await axios.get(`${API}/scheduled-emails`);
      setScheduledEmails(response.data);
    } catch (error) {
      console.error('Error fetching scheduled emails:', error);
    }
  };

  // NOTIFICATION SYSTEM
  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    const notification = { id, message, type, timestamp: new Date() };
    setNotifications(prev => [notification, ...prev.slice(0, 4)]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  // FILE UPLOAD HANDLERS
  const handleSponsorUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus('Processing sponsor file...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/upload-sponsors`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setUploadStatus(response.data.message);
      await fetchSponsors();
      await fetchSponsorStats();
      addNotification('Sponsors uploaded successfully!', 'success');
    } catch (error) {
      const errorMsg = `Error: ${error.response?.data?.detail || error.message}`;
      setUploadStatus(errorMsg);
      addNotification(errorMsg, 'error');
    } finally {
      setIsUploading(false);
    }
  };

  const handleParticipantUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus('Processing participant file...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/upload-participants`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setUploadStatus(response.data.message);
      await fetchParticipants();
      await fetchCertificateStats();
      addNotification('Participants uploaded successfully!', 'success');
    } catch (error) {
      const errorMsg = `Error: ${error.response?.data?.detail || error.message}`;
      setUploadStatus(errorMsg);
      addNotification(errorMsg, 'error');
    } finally {
      setIsUploading(false);
    }
  };

  // EMAIL SENDING HANDLERS
  const sendSponsorEmails = async () => {
    setIsSending(true);
    setSendingStatus('Sending sponsor emails...');

    try {
      const response = await axios.post(`${API}/send-sponsor-emails`);
      setSendingStatus(response.data.message);
      await fetchSponsorStats();
      addNotification('Sponsor emails sent successfully!', 'success');
    } catch (error) {
      const errorMsg = `Error: ${error.response?.data?.detail || error.message}`;
      setSendingStatus(errorMsg);
      addNotification(errorMsg, 'error');
    } finally {
      setIsSending(false);
    }
  };

  const sendCertificates = async () => {
    setIsSending(true);
    setSendingStatus('Generating and sending certificates...');

    try {
      const response = await axios.post(`${API}/send-certificates`);
      setSendingStatus(response.data.message);
      await fetchCertificateStats();
      addNotification('Certificates sent successfully!', 'success');
    } catch (error) {
      const errorMsg = `Error: ${error.response?.data?.detail || error.message}`;
      setSendingStatus(errorMsg);
      addNotification(errorMsg, 'error');
    } finally {
      setIsSending(false);
    }
  };

  // 📧 EMAIL SCHEDULING FUNCTIONS
  const scheduleEmail = async (emailData) => {
    try {
      const response = await axios.post(`${API}/schedule-email`, emailData);
      addNotification('Email scheduled successfully!', 'success');
      fetchScheduledEmails();
      setShowScheduleModal(false);
      resetScheduleForm();
      return response.data;
    } catch (error) {
      console.error('Error scheduling email:', error);
      addNotification('Error scheduling email: ' + error.message, 'error');
      throw error;
    }
  };

  const cancelScheduledEmail = async (emailId) => {
    try {
      await axios.delete(`${API}/scheduled-emails/${emailId}`);
      addNotification('Scheduled email cancelled successfully!', 'success');
      fetchScheduledEmails();
    } catch (error) {
      console.error('Error cancelling scheduled email:', error);
      addNotification('Error cancelling email: ' + error.message, 'error');
    }
  };

  const updateScheduledEmail = async (emailId, updates) => {
    try {
      await axios.put(`${API}/scheduled-emails/${emailId}`, updates);
      addNotification('Scheduled email updated successfully!', 'success');
      fetchScheduledEmails();
    } catch (error) {
      console.error('Error updating scheduled email:', error);
      addNotification('Error updating email: ' + error.message, 'error');
    }
  };

  const resetScheduleForm = () => {
    setScheduleForm({
      recipient_email: '',
      subject: '',
      content: '',
      schedule_date: '',
      schedule_time: '',
      template_type: 'sponsor',
      priority: 'normal',
      recurring: false
    });
  };

  // 📁 DRAG & DROP FUNCTIONS
  const handleDragOver = (e) => {
    e.preventDefault();
    setDragDropArea(prev => ({ ...prev, isDragOver: true }));
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragDropArea(prev => ({ ...prev, isDragOver: false }));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragDropArea(prev => ({ ...prev, isDragOver: false }));
    
    const files = Array.from(e.dataTransfer.files);
    const file = files[0];
    
    if (file && (file.type === 'text/csv' || file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
      processFileUpload(file);
    } else {
      addNotification('Please drop a valid CSV or Excel file', 'error');
    }
  };

  const processFileUpload = async (file) => {
    setDragDropArea(prev => ({ ...prev, isProcessing: true }));
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Preview the file first
      const previewResponse = await axios.post(`${API}/preview-upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setUploadPreviewData(previewResponse.data);
      setShowUploadPreview(true);
    } catch (error) {
      addNotification('Error processing file: ' + error.message, 'error');
    } finally {
      setDragDropArea(prev => ({ ...prev, isProcessing: false }));
    }
  };

  const confirmUpload = async (uploadData) => {
    try {
      const endpoint = uploadData.file_type === 'sponsors' ? 'upload-sponsors' : 'upload-participants';
      const response = await axios.post(`${API}/${endpoint}`, uploadData);
      
      addNotification(response.data.message, 'success');
      
      if (uploadData.file_type === 'sponsors') {
        await fetchSponsors();
        await fetchSponsorStats();
      } else {
        await fetchParticipants();
        await fetchCertificateStats();
      }
      
      setShowUploadPreview(false);
      setUploadPreviewData(null);
    } catch (error) {
      addNotification('Error uploading file: ' + error.message, 'error');
    }
  };

  // RENDER FUNCTIONS
  const renderNavigation = () => (
    <nav className="main-nav">
      <div className="nav-brand">
        <h1>🚀 Hackfinity Platform</h1>
        <div className="nav-controls">
          <button 
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            className="theme-toggle"
            title="Toggle Theme"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
          <div className="notification-bell">
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="notification-btn"
            >
              🔔
              {notifications.length > 0 && <span className="notification-count">{notifications.length}</span>}
            </button>
            {showNotifications && (
              <div className="notifications-dropdown">
                <h4>Notifications</h4>
                {notifications.length === 0 ? (
                  <p>No new notifications</p>
                ) : (
                  notifications.map(notification => (
                    <div key={notification.id} className={`notification-item ${notification.type}`}>
                      <p>{notification.message}</p>
                      <small>{notification.timestamp.toLocaleTimeString()}</small>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="nav-tabs">
        {[
          { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
          { id: 'sponsors', label: '💼 Sponsors', icon: '💼' },
          { id: 'participants', label: '👥 Participants', icon: '👥' },
          { id: 'scheduling', label: '⏰ Email Scheduling', icon: '⏰' },
          { id: 'uploads', label: '📁 Drag & Drop', icon: '📁' },
          { id: 'analytics', label: '📈 Analytics', icon: '📈' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );

  const renderDashboard = () => (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>🚀 Hackfinity Analytics Dashboard</h2>
        <p className="dashboard-subtitle">Monitor your platform performance and statistics</p>
      </div>

      {/* Overview Stats */}
      <div className="stats-overview">
        <div className="stat-card primary">
          <div className="stat-icon">💼</div>
          <div className="stat-content">
            <div className="stat-number">{sponsors.length}</div>
            <div className="stat-label">Total Sponsors</div>
            <div className="stat-change">+12% from last month</div>
          </div>
        </div>
        <div className="stat-card success">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-number">{participants.length}</div>
            <div className="stat-label">Total Participants</div>
            <div className="stat-change">+8% from last month</div>
          </div>
        </div>
        <div className="stat-card warning">
          <div className="stat-icon">📧</div>
          <div className="stat-content">
            <div className="stat-number">{sponsorStats.sent}</div>
            <div className="stat-label">Emails Sent</div>
            <div className="stat-change">+25% from last month</div>
          </div>
        </div>
        <div className="stat-card info">
          <div className="stat-icon">⏰</div>
          <div className="stat-content">
            <div className="stat-number">{scheduledEmails.length}</div>
            <div className="stat-label">Scheduled Emails</div>
            <div className="stat-change">Active schedules</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="dashboard-actions">
        <h3>⚡ Quick Actions</h3>
        <div className="action-grid">
          <button 
            onClick={() => setActiveTab('uploads')}
            className="action-card upload-action"
          >
            <div className="action-icon">📁</div>
            <div className="action-content">
              <h4>Upload Files</h4>
              <p>Drag & drop sponsors or participants</p>
            </div>
          </button>
          <button 
            onClick={() => setShowScheduleModal(true)}
            className="action-card schedule-action"
          >
            <div className="action-icon">⏰</div>
            <div className="action-content">
              <h4>Schedule Email</h4>
              <p>Set up automated email delivery</p>
            </div>
          </button>
          <button 
            onClick={sendSponsorEmails}
            disabled={sponsors.length === 0 || isSending}
            className="action-card send-action"
          >
            <div className="action-icon">📧</div>
            <div className="action-content">
              <h4>Send Sponsor Emails</h4>
              <p>{sponsors.length} sponsors ready</p>
            </div>
          </button>
          <button 
            onClick={sendCertificates}
            disabled={participants.length === 0 || isSending}
            className="action-card certificate-action"
          >
            <div className="action-icon">🏆</div>
            <div className="action-content">
              <h4>Send Certificates</h4>
              <p>{participants.length} participants ready</p>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="recent-activity">
        <h3>🕒 Recent Activity</h3>
        <div className="activity-list">
          <div className="activity-item">
            <span className="activity-icon">📧</span>
            <div className="activity-content">
              <span className="activity-text">{sponsorStats.sent} sponsor emails sent</span>
              <span className="activity-time">Today</span>
            </div>
          </div>
          <div className="activity-item">
            <span className="activity-icon">🏆</span>
            <div className="activity-content">
              <span className="activity-text">{certificateStats.sent} certificates generated</span>
              <span className="activity-time">Today</span>
            </div>
          </div>
          <div className="activity-item">
            <span className="activity-icon">⏰</span>
            <div className="activity-content">
              <span className="activity-text">{scheduledEmails.filter(e => e.status === 'pending').length} emails scheduled</span>
              <span className="activity-time">This week</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSponsors = () => (
    <div className="section sponsors-section">
      <div className="section-header">
        <h2>💼 Sponsor Management</h2>
        <div className="section-actions">
          <input
            type="file"
            id="sponsor-upload"
            accept=".csv,.xlsx,.xls"
            onChange={handleSponsorUpload}
            style={{ display: 'none' }}
            disabled={isUploading}
          />
          <label htmlFor="sponsor-upload" className={`btn btn-primary ${isUploading ? 'disabled' : ''}`}>
            📁 Upload Sponsors
          </label>
          <button
            onClick={sendSponsorEmails}
            disabled={isSending || sponsors.length === 0}
            className="btn btn-success"
          >
            {isSending ? '📤 Sending...' : `📧 Send Emails (${sponsors.length})`}
          </button>
        </div>
      </div>

      {/* Stats cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-number">{sponsorStats.total}</div>
            <div className="stat-label">Total Sponsors</div>
          </div>
        </div>
        <div className="stat-card success">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-number">{sponsorStats.sent}</div>
            <div className="stat-label">Emails Sent</div>
          </div>
        </div>
        <div className="stat-card warning">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <div className="stat-number">{sponsorStats.pending}</div>
            <div className="stat-label">Pending</div>
          </div>
        </div>
        <div className="stat-card error">
          <div className="stat-icon">❌</div>
          <div className="stat-content">
            <div className="stat-number">{sponsorStats.failed}</div>
            <div className="stat-label">Failed</div>
          </div>
        </div>
      </div>

      {/* Status messages */}
      {uploadStatus && (
        <div className={`status-message ${uploadStatus.includes('Error') ? 'error' : 'success'}`}>
          {uploadStatus}
        </div>
      )}

      {sendingStatus && (
        <div className={`status-message ${sendingStatus.includes('Error') ? 'error' : 'success'}`}>
          {sendingStatus}
        </div>
      )}

      {/* Sponsors table */}
      <div className="data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Organization</th>
              <th>Status</th>
              <th>Email Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sponsors.map((sponsor, index) => (
              <tr key={index}>
                <td>{sponsor.name}</td>
                <td>{sponsor.email}</td>
                <td>{sponsor.organization}</td>
                <td>
                  <span className={`status-badge ${sponsor.status || 'pending'}`}>
                    {sponsor.status || 'Pending'}
                  </span>
                </td>
                <td>
                  <span className={`status-badge ${sponsor.email_status || 'pending'}`}>
                    {sponsor.email_status || 'Pending'}
                  </span>
                </td>
                <td>
                  <button className="btn btn-sm btn-secondary">View</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderParticipants = () => (
    <div className="section participants-section">
      <div className="section-header">
        <h2>👥 Participant Management</h2>
        <div className="section-actions">
          <input
            type="file"
            id="participant-upload"
            accept=".csv,.xlsx,.xls"
            onChange={handleParticipantUpload}
            style={{ display: 'none' }}
            disabled={isUploading}
          />
          <label htmlFor="participant-upload" className={`btn btn-primary ${isUploading ? 'disabled' : ''}`}>
            📁 Upload Participants
          </label>
          <button
            onClick={sendCertificates}
            disabled={isSending || participants.length === 0}
            className="btn btn-success"
          >
            {isSending ? '🏆 Generating...' : `🏆 Send Certificates (${participants.length})`}
          </button>
        </div>
      </div>

      {/* Certificate stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-number">{certificateStats.total}</div>
            <div className="stat-label">Total Participants</div>
          </div>
        </div>
        <div className="stat-card success">
          <div className="stat-icon">🏆</div>
          <div className="stat-content">
            <div className="stat-number">{certificateStats.sent}</div>
            <div className="stat-label">Certificates Sent</div>
          </div>
        </div>
        <div className="stat-card warning">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <div className="stat-number">{certificateStats.pending}</div>
            <div className="stat-label">Pending</div>
          </div>
        </div>
        <div className="stat-card error">
          <div className="stat-icon">❌</div>
          <div className="stat-content">
            <div className="stat-number">{certificateStats.failed}</div>
            <div className="stat-label">Failed</div>
          </div>
        </div>
      </div>

      {/* Participants table */}
      <div className="data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Institution</th>
              <th>Status</th>
              <th>Certificate Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {participants.map((participant, index) => (
              <tr key={index}>
                <td>{participant.name}</td>
                <td>{participant.email}</td>
                <td>{participant.institution || 'N/A'}</td>
                <td>
                  <span className={`status-badge ${participant.status || 'active'}`}>
                    {participant.status || 'Active'}
                  </span>
                </td>
                <td>
                  <span className={`status-badge ${participant.certificate_status || 'pending'}`}>
                    {participant.certificate_status || 'Pending'}
                  </span>
                </td>
                <td>
                  <button className="btn btn-sm btn-secondary">View</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  // 📧 EMAIL SCHEDULING COMPONENTS
  const EmailSchedulingModal = ({ isOpen, onClose, onSchedule }) => {
    const [formData, setFormData] = useState({
      recipient_email: '',
      subject: '',
      content: '',
      schedule_date: '',
      schedule_time: '',
      template_type: 'sponsor',
      priority: 'normal'
    });

    const handleSubmit = async (e) => {
      e.preventDefault();
      await onSchedule(formData);
      setFormData({
        recipient_email: '',
        subject: '',
        content: '',
        schedule_date: '',
        schedule_time: '',
        template_type: 'sponsor',
        priority: 'normal'
      });
      onClose();
    };

    if (!isOpen) return null;

    return (
      <div className="modal-overlay">
        <div className="modal-content">
          <div className="modal-header">
            <h3>⏰ Schedule Email</h3>
            <button onClick={onClose} className="modal-close">✕</button>
          </div>
          <form onSubmit={handleSubmit} className="schedule-form">
            <div className="form-group">
              <label>Recipient Email</label>
              <input
                type="email"
                value={formData.recipient_email}
                onChange={(e) => setFormData({...formData, recipient_email: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label>Subject</label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => setFormData({...formData, subject: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label>Content</label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
                rows={4}
                required
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Date</label>
                <input
                  type="date"
                  value={formData.schedule_date}
                  onChange={(e) => setFormData({...formData, schedule_date: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Time</label>
                <input
                  type="time"
                  value={formData.schedule_time}
                  onChange={(e) => setFormData({...formData, schedule_time: e.target.value})}
                  required
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Template Type</label>
                <select
                  value={formData.template_type}
                  onChange={(e) => setFormData({...formData, template_type: e.target.value})}
                >
                  <option value="sponsor">Sponsor</option>
                  <option value="participant">Participant</option>
                  <option value="certificate">Certificate</option>
                  <option value="reminder">Reminder</option>
                </select>
              </div>
              <div className="form-group">
                <label>Priority</label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({...formData, priority: e.target.value})}
                >
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>
            <div className="form-actions">
              <button type="button" onClick={onClose} className="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                Schedule Email
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const ScheduledEmailsList = ({ emails, onUpdate, onCancel }) => {
    if (!emails || emails.length === 0) {
      return (
        <div className="empty-state">
          <div className="empty-icon">📧</div>
          <h3>No scheduled emails</h3>
          <p>Schedule your first email to get started</p>
          <button onClick={() => setShowScheduleModal(true)} className="btn btn-primary">
            Schedule Email
          </button>
        </div>
      );
    }

    return (
      <div className="scheduled-emails-list">
        {emails.map((email) => (
          <div key={email.id} className="scheduled-email-card">
            <div className="email-header">
              <div className="email-badges">
                <span className={`badge status-${email.status || 'pending'}`}>
                  {email.status || 'pending'}
                </span>
                <span className={`badge type-${email.template_type}`}>
                  {email.template_type}
                </span>
                <span className={`badge priority-${email.priority || 'normal'}`}>
                  {email.priority || 'normal'} priority
                </span>
              </div>
              <div className="email-actions">
                <button
                  onClick={() => onUpdate(email.id)}
                  className="btn btn-sm btn-secondary"
                >
                  ✏️ Edit
                </button>
                <button
                  onClick={() => onCancel(email.id)}
                  className="btn btn-sm btn-danger"
                >
                  🗑️ Cancel
                </button>
              </div>
            </div>
            <div className="email-content">
              <h4>{email.subject}</h4>
              <p className="email-recipient">To: {email.recipient_email}</p>
              <p className="email-schedule">
                📅 {email.schedule_date} at {email.schedule_time}
              </p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderScheduling = () => (
    <div className="section scheduling-section">
      <div className="section-header">
        <h2>⏰ Email Scheduling</h2>
        <div className="section-actions">
          <button
            onClick={() => setShowScheduleModal(true)}
            className="btn btn-primary"
          >
            ⏰ Schedule New Email
          </button>
          <button
            onClick={fetchScheduledEmails}
            className="btn btn-secondary"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Email Scheduling Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📧</div>
          <div className="stat-content">
            <div className="stat-number">{scheduledEmails.length}</div>
            <div className="stat-label">Scheduled Emails</div>
          </div>
        </div>
        <div className="stat-card info">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <div className="stat-number">
              {scheduledEmails.filter(e => e.status === 'pending').length}
            </div>
            <div className="stat-label">Pending</div>
          </div>
        </div>
        <div className="stat-card success">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-number">
              {scheduledEmails.filter(e => e.status === 'sent').length}
            </div>
            <div className="stat-label">Sent</div>
          </div>
        </div>
        <div className="stat-card warning">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <div className="stat-number">
              {scheduledEmails.filter(e => e.status === 'failed').length}
            </div>
            <div className="stat-label">Failed</div>
          </div>
        </div>
      </div>

      {/* Scheduled Emails List */}
      <div className="content-card">
        <div className="card-header">
          <h3>📋 Scheduled Emails</h3>
        </div>
        <div className="card-content">
          <ScheduledEmailsList
            emails={scheduledEmails}
            onUpdate={updateScheduledEmail}
            onCancel={cancelScheduledEmail}
          />
        </div>
      </div>
    </div>
  );

  // 📁 DRAG & DROP COMPONENTS
  const DragDropArea = ({ onFileUpload, uploadType, isUploading }) => {
    const [isDragOver, setIsDragOver] = useState(false);

    const handleDragOver = (e) => {
      e.preventDefault();
      setIsDragOver(true);
    };

    const handleDragLeave = (e) => {
      e.preventDefault();
      setIsDragOver(false);
    };

    const handleDrop = (e) => {
      e.preventDefault();
      setIsDragOver(false);
      
      const files = Array.from(e.dataTransfer.files);
      const file = files[0];
      
      if (file && (file.type === 'text/csv' || file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
        onFileUpload(file, uploadType);
      } else {
        addNotification('Please drop a valid CSV or Excel file', 'error');
      }
    };

    const handleFileSelect = (e) => {
      const file = e.target.files[0];
      if (file) {
        onFileUpload(file, uploadType);
      }
    };

    return (
      <div
        className={`drag-drop-area ${isDragOver ? 'drag-over' : ''} ${isUploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="drag-drop-content">
          <div className="drag-drop-icon">
            {isUploading ? '⏳' : '📁'}
          </div>
          <div className="drag-drop-text">
            <p className="drag-drop-title">
              {isUploading ? 'Processing...' : `Drop ${uploadType} file here`}
            </p>
            <p className="drag-drop-subtitle">
              or{' '}
              <label className="file-select-link">
                browse files
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileSelect}
                  disabled={isUploading}
                  style={{ display: 'none' }}
                />
              </label>
            </p>
          </div>
          <p className="drag-drop-formats">
            Supports CSV, XLSX, XLS files (max 10MB)
          </p>
        </div>
      </div>
    );
  };

  const UploadPreview = ({ previewData, onConfirm, onCancel }) => {
    if (!previewData) return null;

    return (
      <div className="modal-overlay">
        <div className="modal-content upload-preview-modal">
          <div className="modal-header">
            <h3>📋 Upload Preview</h3>
            <button onClick={onCancel} className="modal-close">✕</button>
          </div>
          
          <div className="preview-stats">
            <div className="preview-stat">
              <h4>Total Records</h4>
              <p>{previewData.total_records}</p>
            </div>
            <div className="preview-stat">
              <h4>Quality Score</h4>
              <p>{previewData.quality_analysis?.quality_score || 0}%</p>
            </div>
            <div className="preview-stat">
              <h4>Valid Emails</h4>
              <p>{previewData.quality_analysis?.valid_emails || 0}</p>
            </div>
          </div>

          <div className="preview-table-container">
            <h4>Data Preview (First 5 rows)</h4>
            <table className="preview-table">
              <thead>
                <tr>
                  {Object.keys(previewData.processed_data?.[0] || {})
                    .filter(key => key !== 'original_data')
                    .map(key => (
                      <th key={key}>{key}</th>
                    ))}
                </tr>
              </thead>
              <tbody>
                {previewData.processed_data?.slice(0, 5).map((row, index) => (
                  <tr key={index}>
                    {Object.entries(row).map(([key, value]) => (
                      key !== 'original_data' && (
                        <td key={key}>{value || '-'}</td>
                      )
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="preview-actions">
            <button onClick={onCancel} className="btn btn-secondary">
              Cancel
            </button>
            <button onClick={() => onConfirm(previewData)} className="btn btn-primary">
              Confirm Upload
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderUploads = () => (
    <div className="section uploads-section">
      <div className="section-header">
        <h2>📁 Drag & Drop File Upload</h2>
        <p className="section-subtitle">
          Upload sponsor or participant data via drag & drop or file selection
        </p>
      </div>

      <div className="upload-grid">
        {/* Sponsors Upload */}
        <div className="upload-card">
          <div className="card-header">
            <h3>💼 Upload Sponsors</h3>
            <p>Upload sponsor contact information and details</p>
          </div>
          <div className="card-content">
            <DragDropArea
              onFileUpload={processFileUpload}
              uploadType="sponsors"
              isUploading={dragDropArea.isProcessing}
            />
          </div>
        </div>

        {/* Participants Upload */}
        <div className="upload-card">
          <div className="card-header">
            <h3>👥 Upload Participants</h3>
            <p>Upload participant information for certificates</p>
          </div>
          <div className="card-content">
            <DragDropArea
              onFileUpload={processFileUpload}
              uploadType="participants"
              isUploading={dragDropArea.isProcessing}
            />
          </div>
        </div>
      </div>

      {/* Upload Guidelines */}
      <div className="upload-guidelines">
        <h3>📋 Upload Guidelines</h3>
        <div className="guidelines-grid">
          <div className="guideline-item">
            <h4>📊 Required Fields</h4>
            <ul>
              <li><strong>Name:</strong> Full name of the person</li>
              <li><strong>Email:</strong> Valid email address</li>
              <li><strong>Organization:</strong> Company or organization (for sponsors)</li>
            </ul>
          </div>
          <div className="guideline-item">
            <h4>💡 Tips</h4>
            <ul>
              <li>Ensure email addresses are valid</li>
              <li>Use consistent naming conventions</li>
              <li>Include all required fields for best results</li>
              <li>Review the preview before confirming upload</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="section analytics-section">
      <div className="section-header">
        <h2>📈 Analytics & Reports</h2>
        <p className="section-subtitle">
          Detailed insights and performance metrics
        </p>
      </div>

      <div className="analytics-grid">
        <div className="analytics-card">
          <h3>📊 Email Performance</h3>
          <div className="analytics-content">
            <div className="metric">
              <span className="metric-label">Success Rate</span>
              <span className="metric-value">
                {sponsorStats.total > 0 ? Math.round((sponsorStats.sent / sponsorStats.total) * 100) : 0}%
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Total Sent</span>
              <span className="metric-value">{sponsorStats.sent}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Failed</span>
              <span className="metric-value">{sponsorStats.failed}</span>
            </div>
          </div>
        </div>

        <div className="analytics-card">
          <h3>🏆 Certificate Performance</h3>
          <div className="analytics-content">
            <div className="metric">
              <span className="metric-label">Completion Rate</span>
              <span className="metric-value">
                {certificateStats.total > 0 ? Math.round((certificateStats.sent / certificateStats.total) * 100) : 0}%
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Certificates Issued</span>
              <span className="metric-value">{certificateStats.sent}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Pending</span>
              <span className="metric-value">{certificateStats.pending}</span>
            </div>
          </div>
        </div>

        <div className="analytics-card">
          <h3>⏰ Scheduling Insights</h3>
          <div className="analytics-content">
            <div className="metric">
              <span className="metric-label">Active Schedules</span>
              <span className="metric-value">
                {scheduledEmails.filter(e => e.status === 'pending').length}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Completed</span>
              <span className="metric-value">
                {scheduledEmails.filter(e => e.status === 'sent').length}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Success Rate</span>
              <span className="metric-value">
                {scheduledEmails.length > 0 ? 
                  Math.round((scheduledEmails.filter(e => e.status === 'sent').length / scheduledEmails.length) * 100) : 0}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // MAIN RENDER
  return (
    <div className={`app ${theme}`}>
      {renderNavigation()}
      
      <main className="main-content">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'sponsors' && renderSponsors()}
        {activeTab === 'participants' && renderParticipants()}
        {activeTab === 'scheduling' && renderScheduling()}
        {activeTab === 'uploads' && renderUploads()}
        {activeTab === 'analytics' && renderAnalytics()}
      </main>

      {/* Modals */}
      <EmailSchedulingModal
        isOpen={showScheduleModal}
        onClose={() => setShowScheduleModal(false)}
        onSchedule={scheduleEmail}
      />

      <UploadPreview
        previewData={uploadPreviewData}
        onConfirm={confirmUpload}
        onCancel={() => {
          setShowUploadPreview(false);
          setUploadPreviewData(null);
        }}
      />
    </div>
  );
}

export default App;
