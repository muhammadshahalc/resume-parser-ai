import React, { useState } from 'react';
import axios from 'axios';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Divider,
  Grid,
  LinearProgress,
  Paper,
  Typography,
  Alert,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import { CloudUpload, ExpandMore } from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';

const API_URL = "http://localhost:8000/api/parse";

const ResumeParser = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    onDrop: acceptedFiles => {
      setFile(acceptedFiles[0]);
      setResult(null);
      setError(null);
    }
  });

  const handleSubmit = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(API_URL, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setResult(response.data.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderPersonalInfo = () => (
    <Card variant="outlined" sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          👤 Personal Information
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="body1">
              <strong>Name:</strong> {result.name || 'N/A'}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body1">
              <strong>Email:</strong> {result.email || 'N/A'}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body1">
              <strong>Phone:</strong> {result.phone || 'N/A'}
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const renderMatchScore = () => (
    <Card variant="outlined" sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          📊 Match Score
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box sx={{ width: '100%', mr: 2 }}>
            <LinearProgress 
              variant="determinate" 
              value={result.match_score || 0} 
              sx={{ height: 10, borderRadius: 5 }}
            />
          </Box>
          <Typography variant="h5">
            {result.match_score || 0}%
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );

  const renderSkills = () => (
    <Card variant="outlined" sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          🛠️ Skills
        </Typography>
        {result.skills?.length > 0 ? (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {result.skills.map((skill, index) => (
              <Chip key={index} label={skill} variant="outlined" />
            ))}
          </Box>
        ) : (
          <Typography variant="body1">No relevant skills found.</Typography>
        )}
      </CardContent>
    </Card>
  );

  const renderEducation = () => (
    <Card variant="outlined" sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          🎓 Education
        </Typography>
        {result.education?.length > 0 ? (
          <List dense>
            {result.education.map((edu, index) => (
              <ListItem key={index}>
                <ListItemText primary={edu} />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body1">No education details found.</Typography>
        )}
      </CardContent>
    </Card>
  );

  const renderExperience = () => (
    <Card variant="outlined" sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          💼 Experience
        </Typography>
        {result.experience?.length > 0 ? (
          <List dense>
            {result.experience.map((exp, index) => (
              <ListItem key={index}>
                <ListItemText primary={exp} />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body1">No experience ranges found.</Typography>
        )}
      </CardContent>
    </Card>
  );

  const renderFullText = () => (
    <Accordion>
      <AccordionSummary expandIcon={<ExpandMore />}>
        <Typography>📄 Full Resume Text</Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Paper variant="outlined" sx={{ p: 2 }}>
          <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
            {result.full_text || 'No text available'}
          </pre>
        </Paper>
      </AccordionDetails>
    </Accordion>
  );

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        📄 Resume Parser & Matcher
      </Typography>
      <Typography variant="body1" paragraph>
        Upload a resume in PDF or DOCX format. The system will extract details and calculate a match score based on company requirements.
      </Typography>

      <Box {...getRootProps()} sx={{
        border: '2px dashed #ccc',
        borderRadius: 2,
        p: 4,
        textAlign: 'center',
        mb: 3,
        cursor: 'pointer',
        '&:hover': {
          borderColor: 'primary.main',
          backgroundColor: 'action.hover'
        }
      }}>
        <input {...getInputProps()} />
        <CloudUpload fontSize="large" sx={{ mb: 1 }} />
        <Typography variant="h6">Drag & drop resume here</Typography>
        <Typography variant="body2" color="text.secondary">
          or click to select a file (PDF or DOCX)
        </Typography>
        {file && (
          <Typography variant="body2" sx={{ mt: 1 }}>
            Selected: {file.name}
          </Typography>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Button
        variant="contained"
        size="large"
        fullWidth
        onClick={handleSubmit}
        disabled={!file || loading}
        startIcon={loading ? <CircularProgress size={20} /> : null}
      >
        {loading ? 'Processing...' : 'Parse Resume'}
      </Button>

      {result && (
        <Box sx={{ mt: 4 }}>
          {renderPersonalInfo()}
          {renderMatchScore()}
          {renderSkills()}
          {renderEducation()}
          {renderExperience()}
          {renderFullText()}
        </Box>
      )}
    </Container>
  );
};

export default ResumeParser;
