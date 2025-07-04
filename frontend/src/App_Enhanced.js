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

  // Template designer state
  const [templateDesigner, setTemplateDesigner] = useState({
    name: '',
    description: '',
    category_id: '',
    template_type: 'email',
    subject: '',
    content: '',
    html_content: '',
    css_styles: '',
    variables: [],
    color_scheme: { primary: '#6366f1', secondary: '#10b981', accent: '#f59e0b' }
  });

  // Certificate designer state
  const [certificateDesigner, setCertificateDesigner] = useState({
    name: '',
    description: '',
    category: 'achievement',
    page_size: 'A4',
    orientation: 'landscape',
    style: {
      background_color: '#ffffff',
      border_color: '#6366f1',
      border_width: 3,
      primary_color: '#6366f1',
      title_font: 'Helvetica-Bold',
      title_size: 36
    },
    elements: [],
    variables: []
  });

  useEffect(() => {
    fetchDashboardData();
    fetchTemplateCategories();
    fetchAdvancedTemplates();
    fetchCertificateTemplates();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [analyticsRes, sponsorsRes, participantsRes] = await Promise.all([
        axios.get(`${API}/analytics/dashboard`),
        axios.get(`${API}/sponsors`),
        axios.get(`${API}/participants`)
      ]);
      
      setAnalytics(analyticsRes.data);
      setSponsors(sponsorsRes.data);
      setParticipants(participantsRes.data);
      setSponsorStats(analyticsRes.data.sponsors?.overview || {});
      setCertificateStats(analyticsRes.data.certificates?.overview || {});
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const fetchTemplateCategories = async () => {
    try {
      const response = await axios.get(`${API}/templates/categories`);
      setTemplateCategories(response.data);
    } catch (error) {
      console.error('Error fetching template categories:', error);
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

  const handleFileUpload = async (event, type) => {
    const file = event.target.files[0];
    if (!file) return;

    setSelectedFile(file);
    setIsUploading(true);
    setUploadStatus(`Processing ${type} file...`);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const endpoint = type === 'sponsors' ? 'upload-sponsors' : 'upload-participants';
      const response = await axios.post(`${API}/${endpoint}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (type === 'sponsors') {
        setSponsors(response.data.sponsors);
      } else {
        setParticipants(response.data.participants);
      }
      
      setUploadStatus(`Successfully processed ${response.data.total_count} ${type}!`);
      fetchDashboardData();
    } catch (error) {
      setUploadStatus(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const createAdvancedTemplate = async () => {
    try {
      await axios.post(`${API}/templates/advanced`, templateDesigner);
      setShowTemplateDesigner(false);
      fetchAdvancedTemplates();
      setTemplateDesigner({
        name: '',
        description: '',
        category_id: '',
        template_type: 'email',
        subject: '',
        content: '',
        html_content: '',
        css_styles: '',
        variables: [],
        color_scheme: { primary: '#6366f1', secondary: '#10b981', accent: '#f59e0b' }
      });
    } catch (error) {
      console.error('Error creating template:', error);
    }
  };

  const createCertificateTemplate = async () => {
    try {
      await axios.post(`${API}/certificates/templates`, certificateDesigner);
      setShowCertificateDesigner(false);
      fetchCertificateTemplates();
      setCertificateDesigner({
        name: '',
        description: '',
        category: 'achievement',
        page_size: 'A4',
        orientation: 'landscape',
        style: {
          background_color: '#ffffff',
          border_color: '#6366f1',
          border_width: 3,
          primary_color: '#6366f1',
          title_font: 'Helvetica-Bold',
          title_size: 36
        },
        elements: [],
        variables: []
      });
    } catch (error) {
      console.error('Error creating certificate template:', error);
    }
  };

  const previewTemplate = async (templateId) => {
    try {
      const response = await axios.post(`${API}/templates/advanced/${templateId}/preview`);
      setTemplatePreview(response.data.content);
    } catch (error) {
      console.error('Error previewing template:', error);
    }
  };

  const previewCertificate = async (templateId) => {
    try {
      const response = await axios.post(`${API}/certificates/templates/${templateId}/preview`);
      setCertificatePreview(response.data.preview);
    } catch (error) {
      console.error('Error previewing certificate:', error);
    }
  };

  const addCertificateElement = (elementType) => {
    const newElement = {
      id: Date.now().toString(),
      type: elementType,
      content: elementType === 'text' ? 'Sample Text' : '',
      x: 100,
      y: 100,
      width: elementType === 'text' ? null : 200,
      height: elementType === 'text' ? null : 100,
      font_size: elementType === 'text' ? 16 : null,
      font_color: elementType === 'text' ? '#000000' : null,
      background_color: elementType === 'shape' ? '#6366f1' : null,
      z_index: certificateDesigner.elements.length + 1
    };

    setCertificateDesigner(prev => ({
      ...prev,
      elements: [...prev.elements, newElement]
    }));
  };

  const updateCertificateElement = (elementId, updates) => {
    setCertificateDesigner(prev => ({
      ...prev,
      elements: prev.elements.map(el => 
        el.id === elementId ? { ...el, ...updates } : el
      )
    }));
  };

  const removeCertificateElement = (elementId) => {
    setCertificateDesigner(prev => ({
      ...prev,
      elements: prev.elements.filter(el => el.id !== elementId)
    }));
  };

  // Render analytics charts
  const renderAnalyticsCharts = () => {
    if (!analytics) return <div>Loading analytics...</div>;

    return (
      <div className="analytics-dashboard">
        <div className="analytics-overview">
          <div className="stat-card">
            <h3>Total Sponsors</h3>
            <p>{analytics.summary?.total_sponsors || 0}</p>
          </div>
          <div className="stat-card">
            <h3>Total Participants</h3>
            <p>{analytics.summary?.total_participants || 0}</p>
          </div>
          <div className="stat-card">
            <h3>Completion Rate</h3>
            <p>{analytics.summary?.completion_rate || 0}%</p>
          </div>
          <div className="stat-card">
            <h3>Conversion Rate</h3>
            <p>{analytics.summary?.conversion_rate || 0}%</p>
          </div>
        </div>

        <div className="charts-grid">
          {analytics.sponsors?.charts && Object.entries(analytics.sponsors.charts).map(([key, chartData]) => (
            <div key={key} className="chart-container">
              {typeof chartData === 'string' && (
                <Plot
                  data={JSON.parse(chartData).data}
                  layout={JSON.parse(chartData).layout}
                  config={{ responsive: true }}
                  style={{ width: '100%', height: '400px' }}
                />
              )}
            </div>
          ))}
        </div>

        <div className="insights-section">
          <h3>AI-Powered Insights</h3>
          <div className="insights-list">
            {analytics.sponsors?.insights?.map((insight, index) => (
              <div key={index} className="insight-card">
                <p>{insight}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // Render template designer
  const renderTemplateDesigner = () => (
    <Modal 
      isOpen={showTemplateDesigner} 
      onRequestClose={() => setShowTemplateDesigner(false)}
      className="template-designer-modal"
      overlayClassName="modal-overlay"
    >
      <div className="template-designer">
        <h2>Advanced Template Designer</h2>
        
        <div className="designer-form">
          <div className="form-group">
            <label>Template Name</label>
            <input
              type="text"
              value={templateDesigner.name}
              onChange={(e) => setTemplateDesigner(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Enter template name"
            />
          </div>

          <div className="form-group">
            <label>Category</label>
            <Select
              options={templateCategories.map(cat => ({ value: cat.id, label: cat.name }))}
              value={templateCategories.find(cat => cat.id === templateDesigner.category_id)}
              onChange={(option) => setTemplateDesigner(prev => ({ ...prev, category_id: option.value }))}
            />
          </div>

          <div className="form-group">
            <label>Template Type</label>
            <Select
              options={[
                { value: 'email', label: 'Email Template' },
                { value: 'certificate', label: 'Certificate' },
                { value: 'letter', label: 'Letter' },
                { value: 'report', label: 'Report' }
              ]}
              value={{ value: templateDesigner.template_type, label: templateDesigner.template_type }}
              onChange={(option) => setTemplateDesigner(prev => ({ ...prev, template_type: option.value }))}
            />
          </div>

          {templateDesigner.template_type === 'email' && (
            <div className="form-group">
              <label>Email Subject</label>
              <input
                type="text"
                value={templateDesigner.subject}
                onChange={(e) => setTemplateDesigner(prev => ({ ...prev, subject: e.target.value }))}
                placeholder="Enter email subject"
              />
            </div>
          )}

          <div className="form-group">
            <label>Template Content</label>
            <AceEditor
              mode="html"
              theme="monokai"
              value={templateDesigner.content}
              onChange={(value) => setTemplateDesigner(prev => ({ ...prev, content: value }))}
              name="template-content-editor"
              editorProps={{ $blockScrolling: true }}
              height="300px"
              width="100%"
              fontSize={14}
              showPrintMargin={true}
              showGutter={true}
              highlightActiveLine={true}
              setOptions={{
                enableBasicAutocompletion: true,
                enableLiveAutocompletion: true,
                enableSnippets: true,
                showLineNumbers: true,
                tabSize: 2,
              }}
            />
          </div>

          <div className="color-scheme-section">
            <h4>Color Scheme</h4>
            <div className="color-pickers">
              <div className="color-picker">
                <label>Primary Color</label>
                <ChromePicker
                  color={templateDesigner.color_scheme.primary}
                  onChange={(color) => setTemplateDesigner(prev => ({
                    ...prev,
                    color_scheme: { ...prev.color_scheme, primary: color.hex }
                  }))}
                />
              </div>
            </div>
          </div>

          <div className="designer-actions">
            <button onClick={createAdvancedTemplate} className="btn-primary">
              Create Template
            </button>
            <button onClick={() => setShowTemplateDesigner(false)} className="btn-secondary">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </Modal>
  );

  // Render certificate designer
  const renderCertificateDesigner = () => (
    <Modal 
      isOpen={showCertificateDesigner} 
      onRequestClose={() => setShowCertificateDesigner(false)}
      className="certificate-designer-modal"
      overlayClassName="modal-overlay"
    >
      <div className="certificate-designer">
        <h2>Certificate Designer</h2>
        
        <div className="designer-layout">
          <div className="designer-sidebar">
            <div className="form-group">
              <label>Certificate Name</label>
              <input
                type="text"
                value={certificateDesigner.name}
                onChange={(e) => setCertificateDesigner(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter certificate name"
              />
            </div>

            <div className="form-group">
              <label>Page Size</label>
              <Select
                options={[
                  { value: 'A4', label: 'A4' },
                  { value: 'A3', label: 'A3' },
                  { value: 'Letter', label: 'Letter' },
                  { value: 'Custom', label: 'Custom' }
                ]}
                value={{ value: certificateDesigner.page_size, label: certificateDesigner.page_size }}
                onChange={(option) => setCertificateDesigner(prev => ({ ...prev, page_size: option.value }))}
              />
            </div>

            <div className="form-group">
              <label>Orientation</label>
              <Select
                options={[
                  { value: 'landscape', label: 'Landscape' },
                  { value: 'portrait', label: 'Portrait' }
                ]}
                value={{ value: certificateDesigner.orientation, label: certificateDesigner.orientation }}
                onChange={(option) => setCertificateDesigner(prev => ({ ...prev, orientation: option.value }))}
              />
            </div>

            <div className="elements-panel">
              <h4>Add Elements</h4>
              <div className="element-buttons">
                <button onClick={() => addCertificateElement('text')} className="element-btn">
                  📝 Text
                </button>
                <button onClick={() => addCertificateElement('image')} className="element-btn">
                  🖼️ Image
                </button>
                <button onClick={() => addCertificateElement('shape')} className="element-btn">
                  🔵 Shape
                </button>
                <button onClick={() => addCertificateElement('signature')} className="element-btn">
                  ✍️ Signature
                </button>
              </div>
            </div>

            <div className="style-panel">
              <h4>Style Settings</h4>
              <div className="form-group">
                <label>Background Color</label>
                <input
                  type="color"
                  value={certificateDesigner.style.background_color}
                  onChange={(e) => setCertificateDesigner(prev => ({
                    ...prev,
                    style: { ...prev.style, background_color: e.target.value }
                  }))}
                />
              </div>
              <div className="form-group">
                <label>Border Color</label>
                <input
                  type="color"
                  value={certificateDesigner.style.border_color}
                  onChange={(e) => setCertificateDesigner(prev => ({
                    ...prev,
                    style: { ...prev.style, border_color: e.target.value }
                  }))}
                />
              </div>
            </div>
          </div>

          <div className="designer-canvas">
            <div className="canvas-container">
              <div className="certificate-preview">
                {certificatePreview && (
                  <img src={`data:image/png;base64,${certificatePreview}`} alt="Certificate Preview" />
                )}
              </div>
            </div>
          </div>

          <div className="elements-list">
            <h4>Elements</h4>
            {certificateDesigner.elements.map((element) => (
              <div key={element.id} className="element-item">
                <div className="element-info">
                  <span>{element.type}: {element.content || 'Untitled'}</span>
                </div>
                <div className="element-controls">
                  <input
                    type="text"
                    value={element.content}
                    onChange={(e) => updateCertificateElement(element.id, { content: e.target.value })}
                    placeholder="Element content"
                  />
                  <button onClick={() => removeCertificateElement(element.id)} className="btn-danger">
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="designer-actions">
          <button onClick={createCertificateTemplate} className="btn-primary">
            Create Certificate Template
          </button>
          <button onClick={() => setShowCertificateDesigner(false)} className="btn-secondary">
            Cancel
          </button>
        </div>
      </div>
    </Modal>
  );

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="App">
        <header className="app-header">
          <h1>🚀 Hackfinity - Enhanced Automation Platform</h1>
          <nav className="nav-tabs">
            <button 
              className={activeTab === 'dashboard' ? 'active' : ''} 
              onClick={() => setActiveTab('dashboard')}
            >
              📊 Analytics Dashboard
            </button>
            <button 
              className={activeTab === 'sponsors' ? 'active' : ''} 
              onClick={() => setActiveTab('sponsors')}
            >
              💼 Sponsors
            </button>
            <button 
              className={activeTab === 'participants' ? 'active' : ''} 
              onClick={() => setActiveTab('participants')}
            >
              👥 Participants
            </button>
            <button 
              className={activeTab === 'templates' ? 'active' : ''} 
              onClick={() => setActiveTab('templates')}
            >
              📝 Advanced Templates
            </button>
            <button 
              className={activeTab === 'certificates' ? 'active' : ''} 
              onClick={() => setActiveTab('certificates')}
            >
              🏆 Certificate Designer
            </button>
          </nav>
        </header>

        <main className="main-content">
          {activeTab === 'dashboard' && (
            <div className="dashboard-tab">
              <h2>📊 Advanced Analytics Dashboard</h2>
              {renderAnalyticsCharts()}
            </div>
          )}

          {activeTab === 'sponsors' && (
            <div className="sponsors-tab">
              <h2>💼 Sponsor Management</h2>
              <div className="upload-section">
                <input 
                  type="file" 
                  accept=".csv,.xlsx" 
                  onChange={(e) => handleFileUpload(e, 'sponsors')} 
                  disabled={isUploading}
                />
                <button 
                  onClick={() => setShowTemplateDesigner(true)}
                  className="btn-primary"
                >
                  ✨ Create Advanced Template
                </button>
              </div>
              {uploadStatus && <div className="status-message">{uploadStatus}</div>}
              
              <div className="sponsors-list">
                {sponsors.map((sponsor, index) => (
                  <div key={index} className="sponsor-card">
                    <h4>{sponsor.name}</h4>
                    <p>{sponsor.email}</p>
                    <span className={`status ${sponsor.email_status}`}>
                      {sponsor.email_status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'participants' && (
            <div className="participants-tab">
              <h2>👥 Participant Management</h2>
              <div className="upload-section">
                <input 
                  type="file" 
                  accept=".csv,.xlsx" 
                  onChange={(e) => handleFileUpload(e, 'participants')} 
                  disabled={isUploading}
                />
              </div>
              {uploadStatus && <div className="status-message">{uploadStatus}</div>}
              
              <div className="participants-list">
                {participants.map((participant, index) => (
                  <div key={index} className="participant-card">
                    <h4>{participant.name}</h4>
                    <p>{participant.email}</p>
                    <p>Skills: {participant.skills}</p>
                    <span className={`status ${participant.certificate_status}`}>
                      {participant.certificate_status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'templates' && (
            <div className="templates-tab">
              <h2>📝 Advanced Template Management</h2>
              <div className="template-actions">
                <button 
                  onClick={() => setShowTemplateDesigner(true)}
                  className="btn-primary"
                >
                  ✨ Create New Template
                </button>
              </div>
              
              <div className="templates-grid">
                {advancedTemplates.map((template) => (
                  <div key={template.id} className="template-card">
                    <h4>{template.name}</h4>
                    <p>{template.description}</p>
                    <div className="template-meta">
                      <span className="category">{template.category_id}</span>
                      <span className="type">{template.template_type}</span>
                    </div>
                    <div className="template-actions">
                      <button 
                        onClick={() => previewTemplate(template.id)}
                        className="btn-secondary"
                      >
                        👁️ Preview
                      </button>
                      <button className="btn-primary">✏️ Edit</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'certificates' && (
            <div className="certificates-tab">
              <h2>🏆 Certificate Designer</h2>
              <div className="certificate-actions">
                <button 
                  onClick={() => setShowCertificateDesigner(true)}
                  className="btn-primary"
                >
                  ✨ Create New Certificate Template
                </button>
              </div>
              
              <div className="certificates-grid">
                {certificateTemplates.map((template) => (
                  <div key={template.id} className="certificate-card">
                    <h4>{template.name}</h4>
                    <p>{template.description}</p>
                    <div className="certificate-meta">
                      <span className="category">{template.category}</span>
                      <span className="size">{template.page_size} {template.orientation}</span>
                    </div>
                    <div className="certificate-actions">
                      <button 
                        onClick={() => previewCertificate(template.id)}
                        className="btn-secondary"
                      >
                        👁️ Preview
                      </button>
                      <button className="btn-primary">✏️ Edit</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>

        {renderTemplateDesigner()}
        {renderCertificateDesigner()}

        {templatePreview && (
          <Modal 
            isOpen={!!templatePreview} 
            onRequestClose={() => setTemplatePreview('')}
            className="preview-modal"
            overlayClassName="modal-overlay"
          >
            <div className="template-preview">
              <h3>Template Preview</h3>
              <div className="preview-content" dangerouslySetInnerHTML={{ __html: templatePreview }} />
              <button onClick={() => setTemplatePreview('')} className="btn-secondary">
                Close
              </button>
            </div>
          </Modal>
        )}
      </div>
    </DndProvider>
  );
}

export default App;
