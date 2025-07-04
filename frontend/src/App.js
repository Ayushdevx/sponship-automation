import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import Plot from 'react-plotly.js';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, LineElement, PointElement } from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';
import Modal from 'react-modal';
import Select from 'react-select';
import { ChromePicker } from 'react-color';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-html";
import "ace-builds/src-noconflict/theme-monokai";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, LineElement, PointElement);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const API = `${BACKEND_URL}/api`;

// Modal setup
Modal.setAppElement('#root');

function App() {
  // Existing state
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
  const [selectedFile, setSelectedFile] = useState(null);

  // New state for enhanced features
  const [analytics, setAnalytics] = useState(null);
  const [charts, setCharts] = useState({});
  const [templateCategories, setTemplateCategories] = useState([]);
  const [advancedTemplates, setAdvancedTemplates] = useState([]);
  const [certificateTemplates, setCertificateTemplates] = useState([]);
  const [showTemplateDesigner, setShowTemplateDesigner] = useState(false);
  const [showCertificateDesigner, setShowCertificateDesigner] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [templatePreview, setTemplatePreview] = useState('');
  const [certificatePreview, setCertificatePreview] = useState('');
  const [dashboardWidgets, setDashboardWidgets] = useState({});
  const [selectedChartType, setSelectedChartType] = useState('3d_scatter');
  const [chartLoading, setChartLoading] = useState(false);

  // Template/Certificate designer state
  const [builderConfig, setBuilderConfig] = useState(null);
  const [certificateBuilderConfig, setCertificateBuilderConfig] = useState(null);
  const [designerMode, setDesignerMode] = useState('visual'); // visual, code
  const [selectedElement, setSelectedElement] = useState(null);

  // New state for email scheduling
  const [scheduledEmails, setScheduledEmails] = useState([]);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [scheduleForm, setScheduleForm] = useState({
    recipient_email: '',
    subject: '',
    content: '',
    schedule_date: '',
    schedule_time: '',
    template_type: 'sponsor'
  });
  const [bulkScheduleForm, setBulkScheduleForm] = useState({
    emails: [],
    subject: '',
    content: '',
    schedule_date: '',
    schedule_time: '',
    template_type: 'sponsor'
  });

  // New state for drag & drop functionality
  const [dragDropArea, setDragDropArea] = useState({
    isDragOver: false,
    uploadProgress: 0,
    isProcessing: false
  });
  const [uploadValidation, setUploadValidation] = useState(null);
  const [showUploadPreview, setShowUploadPreview] = useState(false);
  const [uploadPreviewData, setUploadPreviewData] = useState(null);

  useEffect(() => {
    fetchInitialData();
    fetchDashboardWidgets();
    
    // Refresh stats every 5 seconds when sending
    const interval = setInterval(() => {
      if (isSending) {
        fetchSponsorStats();
        fetchCertificateStats();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [isSending]);

  const fetchInitialData = async () => {
    try {
      await Promise.all([
        fetchSponsors(),
        fetchParticipants(),
        fetchTemplates(),
        fetchSponsorStats(),
        fetchCertificateStats(),
        fetchAnalytics(),
        fetchAdvancedTemplates(),
        fetchCertificateTemplates(),
        fetchBuilderConfigs()
      ]);
    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API}/analytics/sponsors`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const fetchAdvancedTemplates = async () => {
    try {
      const response = await axios.get(`${API}/templates/advanced`);
      setAdvancedTemplates(response.data);
    } catch (error) {
      console.error('Error fetching advanced templates:', error);
    }
  };

  const fetchCertificateTemplates = async () => {
    try {
      const response = await axios.get(`${API}/certificates/templates`);
      setCertificateTemplates(response.data);
    } catch (error) {
      console.error('Error fetching certificate templates:', error);
    }
  };

  const fetchBuilderConfigs = async () => {
    try {
      const [templateConfig, certificateConfig] = await Promise.all([
        axios.get(`${API}/templates/builder-config`),
        axios.get(`${API}/certificates/builder-config`)
      ]);
      setBuilderConfig(templateConfig.data);
      setCertificateBuilderConfig(certificateConfig.data);
    } catch (error) {
      console.error('Error fetching builder configs:', error);
    }
  };

  const fetchDashboardWidgets = async () => {
    try {
      const response = await axios.get(`${API}/analytics/dashboard-widgets`);
      setDashboardWidgets(response.data);
    } catch (error) {
      console.error('Error fetching dashboard widgets:', error);
    }
  };

  const fetchAdvancedChart = async (chartType, dataSource = 'sponsors') => {
    setChartLoading(true);
    try {
      const response = await axios.get(`${API}/charts/advanced/${chartType}?data_source=${dataSource}`);
      setCharts(prev => ({
        ...prev,
        [chartType]: response.data
      }));
    } catch (error) {
      console.error(`Error fetching ${chartType} chart:`, error);
    } finally {
      setChartLoading(false);
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

  const handleSponsorUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setSelectedFile(file);
    setIsUploading(true);
    setUploadStatus('Processing sponsor file and generating AI emails...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/upload-sponsors`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setUploadStatus(response.data.message);
      await fetchSponsors();
      await fetchSponsorStats();
    } catch (error) {
      setUploadStatus(`Error: ${error.response?.data?.detail || error.message}`);
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
    } catch (error) {
      setUploadStatus(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const sendSponsorEmails = async () => {
    setIsSending(true);
    setSendingStatus('Sending sponsor emails...');

    try {
      const response = await axios.post(`${API}/send-sponsor-emails`);
      setSendingStatus(response.data.message);
      await fetchSponsorStats();
    } catch (error) {
      setSendingStatus(`Error: ${error.response?.data?.detail || error.message}`);
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
    } catch (error) {
      setSendingStatus(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsSending(false);
    }
  };

  // Email scheduling functions
  const fetchScheduledEmails = async () => {
    try {
      const response = await axios.get(`${API}/scheduled-emails`);
      setScheduledEmails(response.data);
    } catch (error) {
      console.error('Error fetching scheduled emails:', error);
    }
  };

  const scheduleEmail = async (emailData) => {
    try {
      const response = await axios.post(`${API}/schedule-email`, emailData);
      setUploadStatus('Email scheduled successfully!');
      fetchScheduledEmails();
      setShowScheduleModal(false);
      resetScheduleForm();
      return response.data;
    } catch (error) {
      console.error('Error scheduling email:', error);
      setUploadStatus('Error scheduling email: ' + error.message);
      throw error;
    }
  };

  const scheduleBulkEmails = async (bulkData) => {
    try {
      const response = await axios.post(`${API}/schedule-bulk-emails`, bulkData);
      setUploadStatus(`${response.data.scheduled_email_ids.length} emails scheduled successfully!`);
      fetchScheduledEmails();
      return response.data;
    } catch (error) {
      console.error('Error scheduling bulk emails:', error);
      setUploadStatus('Error scheduling bulk emails: ' + error.message);
      throw error;
    }
  };

  const cancelScheduledEmail = async (emailId) => {
    try {
      await axios.delete(`${API}/scheduled-emails/${emailId}`);
      setUploadStatus('Scheduled email cancelled successfully!');
      fetchScheduledEmails();
    } catch (error) {
      console.error('Error cancelling scheduled email:', error);
      setUploadStatus('Error cancelling email: ' + error.message);
    }
  };

  const updateScheduledEmail = async (emailId, updates) => {
    try {
      await axios.put(`${API}/scheduled-emails/${emailId}`, updates);
      setUploadStatus('Scheduled email updated successfully!');
      fetchScheduledEmails();
    } catch (error) {
      console.error('Error updating scheduled email:', error);
      setUploadStatus('Error updating email: ' + error.message);
    }
  };

  const resetScheduleForm = () => {
    setScheduleForm({
      recipient_email: '',
      subject: '',
      content: '',
      schedule_date: '',
      schedule_time: '',
      template_type: 'sponsor'
    });
  };

  // Drag & Drop functions
  const handleDragOver = (e) => {
    e.preventDefault();
    setDragDropArea(prev => ({ ...prev, isDragOver: true }));
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragDropArea(prev => ({ ...prev, isDragOver: false }));
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setDragDropArea(prev => ({ ...prev, isDragOver: false, isProcessing: true }));
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length === 0) return;
    
    const file = files[0];
    
    // Validate file type
    if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      setUploadStatus('Please upload only CSV or Excel files');
      setDragDropArea(prev => ({ ...prev, isProcessing: false }));
      return;
    }
    
    await processDroppedFile(file);
  };

  const processDroppedFile = async (file) => {
    try {
      // First validate the file
      const validationFormData = new FormData();
      validationFormData.append('file', file);
      
      const validationResponse = await axios.post(`${API}/validate-excel-upload`, validationFormData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setUploadValidation(validationResponse.data);
      
      if (validationResponse.data.valid) {
        setUploadPreviewData(validationResponse.data);
        setShowUploadPreview(true);
      } else {
        setUploadStatus(`File validation failed: ${validationResponse.data.error}`);
      }
    } catch (error) {
      console.error('Error validating file:', error);
      setUploadStatus('Error validating file: ' + error.message);
    } finally {
      setDragDropArea(prev => ({ ...prev, isProcessing: false }));
    }
  };

  const confirmFileUpload = async (uploadType = 'sponsors', autoProcess = true) => {
    if (!uploadPreviewData) return;
    
    try {
      setIsUploading(true);
      const formData = new FormData();
      
      // Create a new file from the preview data for upload
      const file = new File([JSON.stringify(uploadPreviewData.preview_data)], uploadPreviewData.filename, {
        type: 'application/json'
      });
      
      formData.append('file', file);
      formData.append('upload_type', uploadType);
      formData.append('auto_process', autoProcess);
      
      const response = await axios.post(`${API}/upload-excel-drag-drop`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setDragDropArea(prev => ({ ...prev, uploadProgress: progress }));
        }
      });
      
      setUploadStatus(`Successfully processed ${response.data.total_records} records!`);
      
      // Refresh data based on upload type
      if (uploadType === 'sponsors') {
        fetchSponsors();
        fetchSponsorStats();
      } else if (uploadType === 'participants') {
        fetchParticipants();
        fetchCertificateStats();
      }
      
      setShowUploadPreview(false);
      setUploadPreviewData(null);
      
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus('Error uploading file: ' + error.message);
    } finally {
      setIsUploading(false);
      setDragDropArea(prev => ({ ...prev, uploadProgress: 0 }));
    }
  };

  // Enhanced navigation tabs
  const renderNavigation = () => (
    <nav className="main-nav">
      <div className="nav-brand">
        <h1>🚀 Hackfinity Platform</h1>
      </div>
      <div className="nav-tabs">
        {[
          { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
          { id: 'sponsors', label: '💼 Sponsors', icon: '💼' },
          { id: 'participants', label: '👥 Participants', icon: '👥' },
          { id: 'scheduling', label: '⏰ Email Scheduling', icon: '⏰' },
          { id: 'uploads', label: '📁 Drag & Drop', icon: '📁' },
          { id: 'templates', label: '📄 Templates', icon: '📄' },
          { id: 'certificates', label: '🏆 Certificates', icon: '🏆' },
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

  // Enhanced sponsors section with improved UI
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
            📧 Send Emails ({sponsors.length})
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

  // Enhanced participants section
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
            🏆 Send Certificates ({participants.length})
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

  // Enhanced Dashboard Component
  const renderDashboard = () => (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>🚀 Hackfinity Analytics Dashboard</h2>
        <div className="dashboard-controls">
          <select 
            value={selectedChartType} 
            onChange={(e) => setSelectedChartType(e.target.value)}
            className="chart-selector"
          >
            <option value="3d_scatter">3D Scatter Plot</option>
            <option value="treemap">Treemap</option>
            <option value="sunburst">Sunburst</option>
            <option value="sankey">Sankey Diagram</option>
            <option value="radar">Radar Chart</option>
            <option value="waterfall">Waterfall</option>
            <option value="gauge">Gauge Chart</option>
            <option value="parallel_coordinates">Parallel Coordinates</option>
            <option value="animated_bar">Animated Bar Chart</option>
          </select>
          <button 
            onClick={() => fetchAdvancedChart(selectedChartType)}
            className="btn-primary"
            disabled={chartLoading}
          >
            {chartLoading ? 'Loading...' : 'Load Chart'}
          </button>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Key Metrics */}
        <div className="widget metrics-widget">
          <h3>📊 Key Metrics</h3>
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-value">{sponsorStats.total}</span>
              <span className="metric-label">Total Sponsors</span>
            </div>
            <div className="metric-card">
              <span className="metric-value">{sponsorStats.sent}</span>
              <span className="metric-label">Emails Sent</span>
            </div>
            <div className="metric-card">
              <span className="metric-value">{certificateStats.total}</span>
              <span className="metric-label">Certificates</span>
            </div>
            <div className="metric-card">
              <span className="metric-value">{analytics?.metrics?.conversion_rate || 0}%</span>
              <span className="metric-label">Conversion Rate</span>
            </div>
          </div>
        </div>

        {/* Advanced Chart Widget */}
        <div className="widget chart-widget large">
          <h3>📈 Advanced Visualization: {selectedChartType.replace('_', ' ').toUpperCase()}</h3>
          {charts[selectedChartType] && charts[selectedChartType].chart ? (
            <Plot
              data={JSON.parse(charts[selectedChartType].chart).data}
              layout={JSON.parse(charts[selectedChartType].chart).layout}
              style={{ width: '100%', height: '400px' }}
            />
          ) : (
            <div className="chart-placeholder">
              <p>Select a chart type and click "Load Chart" to view visualization</p>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="widget actions-widget">
          <h3>⚡ Quick Actions</h3>
          <div className="action-buttons">
            <button 
              onClick={() => setShowTemplateDesigner(true)}
              className="action-btn template-btn"
            >
              🎨 Design Template
            </button>
            <button 
              onClick={() => setShowCertificateDesigner(true)}
              className="action-btn certificate-btn"
            >
              🏆 Create Certificate
            </button>
            <button 
              onClick={() => setActiveTab('analytics')}
              className="action-btn analytics-btn"
            >
              📊 View Analytics
            </button>
            <button 
              onClick={() => setActiveTab('sponsors')}
              className="action-btn sponsor-btn"
            >
              💼 Manage Sponsors
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="widget activity-widget">
          <h3>🕒 Recent Activity</h3>
          <div className="activity-list">
            <div className="activity-item">
              <span className="activity-icon">📧</span>
              <span className="activity-text">5 sponsor emails sent</span>
              <span className="activity-time">2 minutes ago</span>
            </div>
            <div className="activity-item">
              <span className="activity-icon">🏆</span>
              <span className="activity-text">New certificate template created</span>
              <span className="activity-time">15 minutes ago</span>
            </div>
            <div className="activity-item">
              <span className="activity-icon">📊</span>
              <span className="activity-text">Analytics report generated</span>
              <span className="activity-time">1 hour ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Enhanced Analytics Component
  const renderAnalytics = () => (
    <div className="analytics-container">
      <h2>📊 Advanced Analytics & Charts</h2>
      
      <div className="chart-gallery">
        {['3d_scatter', 'treemap', 'sunburst', 'sankey', 'radar', 'waterfall', 'gauge', 'parallel_coordinates'].map(chartType => (
          <div key={chartType} className="chart-card">
            <div className="chart-header">
              <h3>{chartType.replace('_', ' ').toUpperCase()}</h3>
              <button 
                onClick={() => fetchAdvancedChart(chartType)}
                className="btn-secondary"
                disabled={chartLoading}
              >
                Load
              </button>
            </div>
            <div className="chart-content">
              {charts[chartType] && charts[chartType].chart ? (
                <Plot
                  data={JSON.parse(charts[chartType].chart).data}
                  layout={JSON.parse(charts[chartType].chart).layout}
                  style={{ width: '100%', height: '300px' }}
                />
              ) : (
                <div className="chart-placeholder">
                  <p>Click "Load" to view this chart</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  // Enhanced Template Designer Modal
  const renderTemplateDesigner = () => (
    <Modal
      isOpen={showTemplateDesigner}
      onRequestClose={() => setShowTemplateDesigner(false)}
      className="designer-modal"
      overlayClassName="designer-overlay"
    >
      <div className="designer-container">
        <div className="designer-header">
          <h2>🎨 Advanced Template Designer</h2>
          <div className="designer-controls">
            <button 
              onClick={() => setDesignerMode(designerMode === 'visual' ? 'code' : 'visual')}
              className="btn-secondary"
            >
              {designerMode === 'visual' ? 'Code View' : 'Visual View'}
            </button>
            <button onClick={() => setShowTemplateDesigner(false)} className="btn-close">×</button>
          </div>
        </div>

        <div className="designer-content">
          {designerMode === 'visual' ? (
            <div className="visual-designer">
              <div className="designer-sidebar">
                <h3>Components</h3>
                {builderConfig?.components && Object.entries(builderConfig.components).map(([type, config]) => (
                  <div key={type} className="component-item" draggable>
                    <span className="component-icon">{config.icon}</span>
                    <span className="component-name">{config.name}</span>
                  </div>
                ))}
              </div>
              
              <div className="designer-canvas">
                <div className="canvas-area">
                  {/* Canvas for drag-and-drop template building */}
                  <div className="canvas-placeholder">
                    <p>Drag components here to build your template</p>
                  </div>
                </div>
              </div>

              <div className="properties-panel">
                <h3>Properties</h3>
                {selectedElement ? (
                  <div className="element-properties">
                    <p>Configure properties for selected element</p>
                  </div>
                ) : (
                  <p>Select an element to edit properties</p>
                )}
              </div>
            </div>
          ) : (
            <div className="code-designer">
              <AceEditor
                mode="html"
                theme="monokai"
                width="100%"
                height="500px"
                fontSize={14}
                showGutter={true}
                highlightActiveLine={true}
                value={templatePreview}
                onChange={setTemplatePreview}
                setOptions={{
                  enableBasicAutocompletion: true,
                  enableLiveAutocompletion: true,
                  enableSnippets: true,
                  showLineNumbers: true,
                  tabSize: 2,
                }}
              />
            </div>
          )}
        </div>

        <div className="designer-footer">
          <button className="btn-secondary">Save Template</button>
          <button className="btn-primary">Preview</button>
        </div>
      </div>
    </Modal>
  );

  // Enhanced Certificate Designer Modal
  const renderCertificateDesigner = () => (
    <Modal
      isOpen={showCertificateDesigner}
      onRequestClose={() => setShowCertificateDesigner(false)}
      className="designer-modal"
      overlayClassName="designer-overlay"
    >
      <div className="designer-container">
        <div className="designer-header">
          <h2>🏆 Advanced Certificate Designer</h2>
          <div className="designer-controls">
            <select className="layout-selector">
              <option>Classic Layout</option>
              <option>Modern Layout</option>
              <option>Elegant Layout</option>
              <option>Corporate Layout</option>
              <option>Creative Layout</option>
            </select>
            <button onClick={() => setShowCertificateDesigner(false)} className="btn-close">×</button>
          </div>
        </div>

        <div className="certificate-designer-content">
          <div className="certificate-sidebar">
            <h3>Elements</h3>
            {certificateBuilderConfig?.elements && Object.entries(certificateBuilderConfig.elements).map(([type, config]) => (
              <div key={type} className="element-item" draggable>
                <span className="element-icon">{config.icon}</span>
                <span className="element-name">{config.name}</span>
              </div>
            ))}
            
            <h3>Layouts</h3>
            {certificateBuilderConfig?.layouts && Object.entries(certificateBuilderConfig.layouts).map(([type, layout]) => (
              <div key={type} className="layout-item">
                <img src={layout.preview} alt={layout.name} className="layout-preview" />
                <span className="layout-name">{layout.name}</span>
              </div>
            ))}
          </div>
          
          <div className="certificate-canvas">
            <div className="certificate-preview">
              <div className="certificate-page">
                {/* Certificate design canvas */}
                <div className="certificate-placeholder">
                  <p>Design your certificate here</p>
                </div>
              </div>
            </div>
          </div>

          <div className="certificate-properties">
            <h3>Properties</h3>
            <div className="property-group">
              <label>Background Color</label>
              <ChromePicker />
            </div>
            <div className="property-group">
              <label>Border Style</label>
              <select>
                <option>Solid</option>
                <option>Dashed</option>
                <option>Dotted</option>
              </select>
            </div>
          </div>
        </div>

        <div className="designer-footer">
          <button className="btn-secondary">Save Certificate</button>
          <button className="btn-primary">Generate Preview</button>
        </div>
      </div>
    </Modal>
  );

  // Email Scheduling Modal Component
  const EmailSchedulingModal = ({ isOpen, onClose, onSchedule }) => {
    const [formData, setFormData] = useState({
      recipient_email: '',
      subject: '',
      content: '',
      schedule_date: '',
      schedule_time: '',
      template_type: 'sponsor'
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
        template_type: 'sponsor'
      });
      onClose();
    };

    if (!isOpen) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-gray-800">Schedule Email</h3>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Recipient Email
              </label>
              <input
                type="email"
                value={formData.recipient_email}
                onChange={(e) => setFormData({...formData, recipient_email: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subject
              </label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => setFormData({...formData, subject: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Content
              </label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date
                </label>
                <input
                  type="date"
                  value={formData.schedule_date}
                  onChange={(e) => setFormData({...formData, schedule_date: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Time
                </label>
                <input
                  type="time"
                  value={formData.schedule_time}
                  onChange={(e) => setFormData({...formData, schedule_time: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Template Type
              </label>
              <select
                value={formData.template_type}
                onChange={(e) => setFormData({...formData, template_type: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="sponsor">Sponsor</option>
                <option value="participant">Participant</option>
                <option value="certificate">Certificate</option>
                <option value="reminder">Reminder</option>
              </select>
            </div>
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Schedule Email
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  // Drag & Drop Area Component
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
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        onFileUpload(files[0], uploadType);
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
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragOver
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        } ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center space-y-4">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <div>
            <p className="text-lg font-medium text-gray-700">
              {isUploading ? 'Processing...' : `Drop ${uploadType} file here`}
            </p>
            <p className="text-sm text-gray-500">
              or{' '}
              <label className="text-blue-600 cursor-pointer hover:text-blue-700">
                browse files
                <input
                  type="file"
                  className="hidden"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileSelect}
                  disabled={isUploading}
                />
              </label>
            </p>
          </div>
          <p className="text-xs text-gray-400">
            Supports CSV, XLSX, XLS files (max 10MB)
          </p>
        </div>
      </div>
    );
  };

  // Upload Preview Component
  const UploadPreview = ({ previewData, onConfirm, onCancel }) => {
    if (!previewData) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-gray-800">Upload Preview</h3>
            <button
              onClick={onCancel}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          
          <div className="mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-800">Total Records</h4>
                <p className="text-2xl font-bold text-blue-600">{previewData.total_records}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-green-800">Quality Score</h4>
                <p className="text-2xl font-bold text-green-600">
                  {previewData.quality_analysis?.quality_score || 0}%
                </p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h4 className="font-semibold text-yellow-800">Detected Fields</h4>
                <p className="text-2xl font-bold text-yellow-600">
                  {previewData.column_analysis?.detected_fields?.length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <h4 className="font-semibold text-gray-800 mb-2">Data Preview</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border border-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {previewData.processed_data?.[0] && Object.keys(previewData.processed_data[0]).map(key => (
                      key !== 'original_data' && (
                        <th key={key} className="px-4 py-2 text-left text-sm font-medium text-gray-700 border-b">
                          {key.charAt(0).toUpperCase() + key.slice(1)}
                        </th>
                      )
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {previewData.processed_data?.slice(0, 5).map((row, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      {Object.entries(row).map(([key, value]) => (
                        key !== 'original_data' && (
                          <td key={key} className="px-4 py-2 text-sm text-gray-600 border-b">
                            {value || '-'}
                          </td>
                        )
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {previewData.quality_analysis?.recommendations && (
            <div className="mb-6">
              <h4 className="font-semibold text-gray-800 mb-2">Recommendations</h4>
              <ul className="list-disc list-inside space-y-1">
                {previewData.quality_analysis.recommendations
                  .filter(rec => rec) // Remove null recommendations
                  .map((rec, index) => (
                    <li key={index} className="text-sm text-gray-600">{rec}</li>
                  ))}
              </ul>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button
              onClick={onCancel}
              className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={() => onConfirm(previewData)}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              Confirm Upload
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Scheduled Emails List Component
  const ScheduledEmailsList = ({ emails, onUpdate, onCancel }) => {
    if (!emails || emails.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          No scheduled emails found
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {emails.map((email) => (
          <div key={email.id} className="bg-white border rounded-lg p-4 shadow-sm">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    email.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    email.status === 'sent' ? 'bg-green-100 text-green-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {email.status || 'pending'}
                  </span>
                  <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                    {email.template_type}
                  </span>
                </div>
                <h4 className="font-semibold text-gray-800">{email.subject}</h4>
                <p className="text-sm text-gray-600">To: {email.recipient_email}</p>
                <p className="text-sm text-gray-500">
                  Scheduled: {email.schedule_date} at {email.schedule_time}
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => onUpdate(email.id)}
                  className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                >
                  Edit
                </button>
                <button
                  onClick={() => onCancel(email.id)}
                  className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Email Scheduling Section
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
          <h3>Scheduled Emails</h3>
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

  // Drag & Drop Upload Section
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
              onFileUpload={handleDragDropUpload}
              uploadType="sponsors"
              isUploading={dragDropArea.isUploading && dragDropArea.uploadType === 'sponsors'}
            />
            {dragDropArea.uploadStatus && dragDropArea.uploadType === 'sponsors' && (
              <div className={`upload-status ${dragDropArea.uploadStatus.includes('Error') ? 'error' : 'success'}`}>
                {dragDropArea.uploadStatus}
              </div>
            )}
          </div>
        </div>

        {/* Participants Upload */}
        <div className="upload-card">
          <div className="card-header">
            <h3>👥 Upload Participants</h3>
            <p>Upload participant information for certificate generation</p>
          </div>
          <div className="card-content">
            <DragDropArea
              onFileUpload={handleDragDropUpload}
              uploadType="participants"
              isUploading={dragDropArea.isUploading && dragDropArea.uploadType === 'participants'}
            />
            {dragDropArea.uploadStatus && dragDropArea.uploadType === 'participants' && (
              <div className={`upload-status ${dragDropArea.uploadStatus.includes('Error') ? 'error' : 'success'}`}>
                {dragDropArea.uploadStatus}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Upload Guidelines */}
      <div className="content-card">
        <div className="card-header">
          <h3>📋 Upload Guidelines</h3>
        </div>
        <div className="card-content">
          <div className="guidelines-grid">
            <div className="guideline-item">
              <h4>📄 Supported Formats</h4>
              <ul>
                <li>CSV files (.csv)</li>
                <li>Excel files (.xlsx, .xls)</li>
                <li>Maximum file size: 10MB</li>
              </ul>
            </div>
            <div className="guideline-item">
              <h4>📊 Required Columns</h4>
              <ul>
                <li><strong>Name:</strong> Full name or contact name</li>
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
    </div>
  );

  // Main render function
  return (
    <DndProvider backend={HTML5Backend}>
      <div className="app">
        {renderNavigation()}
        
        <main className="main-content">
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'sponsors' && renderSponsors()}
          {activeTab === 'participants' && renderParticipants()}
          {activeTab === 'scheduling' && renderScheduling()}
          {activeTab === 'uploads' && renderUploads()}
          {activeTab === 'analytics' && renderAnalytics()}
          {activeTab === 'templates' && (
            <div className="section">
              <h2>📄 Template Management</h2>
              <button 
                onClick={() => setShowTemplateDesigner(true)}
                className="btn btn-primary"
              >
                🎨 Create New Template
              </button>
              {/* Template list will go here */}
            </div>
          )}
          {activeTab === 'certificates' && (
            <div className="section">
              <h2>🏆 Certificate Management</h2>
              <button 
                onClick={() => setShowCertificateDesigner(true)}
                className="btn btn-primary"
              >
                🏆 Design Certificate
              </button>
              {/* Certificate templates list will go here */}
            </div>
          )}
          {activeTab === 'scheduling' && renderScheduling()}
          {activeTab === 'uploads' && renderUploads()}
        </main>

        {/* Designer Modals */}
        {renderTemplateDesigner()}
        {renderCertificateDesigner()}

        {/* Email Scheduling Modal */}
        <EmailSchedulingModal
          isOpen={showScheduleModal}
          onClose={() => setShowScheduleModal(false)}
          onSchedule={scheduleEmail}
        />

        {/* Upload Preview Modal */}
        <UploadPreview
          previewData={dragDropArea.previewData}
          onConfirm={confirmUpload}
          onCancel={() => setDragDropArea(prev => ({ ...prev, previewData: null }))}
        />
      </div>
    </DndProvider>
  );
}

export default App;