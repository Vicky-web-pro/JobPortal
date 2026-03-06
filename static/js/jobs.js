/**
 * JobPortal - Jobs Page JavaScript
 * Handles dynamic job loading and filtering
 */

let allJobs = [];

// Load jobs on page load
document.addEventListener('DOMContentLoaded', function() {
    loadJobs();
    
    // Get URL parameters for pre-filling search
    const urlParams = new URLSearchParams(window.location.search);
    const keyword = urlParams.get('keyword');
    const location = urlParams.get('location');
    
    if (keyword) {
        document.getElementById('searchInput').value = keyword;
    }
    if (location) {
        document.getElementById('locationInput').value = location;
    }
    
    // Apply initial filter if params exist
    if (keyword || location) {
        filterJobs();
    }
});

function loadJobs() {
    const loading = document.getElementById('loading');
    const jobsList = document.getElementById('jobsList');
    
    fetch('/api/jobs')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            allJobs = data;
            displayJobs(data);
            
            if (loading) {
                loading.style.display = 'none';
            }
            
            // Update jobs count
            const jobsCount = document.getElementById('jobsCount');
            if (jobsCount) {
                jobsCount.textContent = data.length;
            }
        })
        .catch(error => {
            console.error('Error loading jobs:', error);
            if (loading) {
                loading.innerHTML = '<p>Error loading jobs. Please try again later.</p>';
            }
        });
}

function displayJobs(jobs) {
    const jobsList = document.getElementById('jobsList');
    const noResults = document.getElementById('noResults');
    const jobsCount = document.getElementById('jobsCount');
    
    if (!jobsList) return;
    
    jobsList.innerHTML = '';
    
    if (jobs.length === 0) {
        if (noResults) noResults.style.display = 'block';
        return;
    }
    
    if (noResults) noResults.style.display = 'none';
    
    if (jobsCount) {
        jobsCount.textContent = jobs.length;
    }
    
    jobs.forEach(job => {
        const jobCard = createJobCard(job);
        jobsList.innerHTML += jobCard;
    });
}

function createJobCard(job) {
    return `
        <div class="job-card">
            <div class="job-header">
                <div class="job-title">
                    <h3>${job.title}</h3>
                    <span class="job-type">${job.job_type}</span>
                </div>
            </div>
            <div class="job-company">
                <h4><i class="fas fa-building"></i> ${job.company}</h4>
            </div>
            <div class="job-details">
                <span><i class="fas fa-map-marker-alt"></i> ${job.location}</span>
                <span><i class="fas fa-money-b-wave"></i> ${job.salary}</span>
                <span><i class="fas fa-layer-group"></i> ${job.department}</span>
            </div>
            <div class="job-footer">
                <a href="/apply/${job.id}" class="btn btn-primary">Apply Now</a>
            </div>
        </div>
    `;
}

function filterJobs() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const locationTerm = document.getElementById('locationInput')?.value.toLowerCase() || '';
    
    const filtered = allJobs.filter(job => {
        const matchesSearch = !searchTerm || 
            job.title.toLowerCase().includes(searchTerm) ||
            job.company.toLowerCase().includes(searchTerm) ||
            job.job_role.toLowerCase().includes(searchTerm) ||
            job.department.toLowerCase().includes(searchTerm) ||
            (job.description && job.description.toLowerCase().includes(searchTerm));
        
        const matchesLocation = !locationTerm || 
            job.location.toLowerCase().includes(locationTerm);
        
        return matchesSearch && matchesLocation;
    });
    
    displayJobs(filtered);
}

// Search on Enter key
const searchInput = document.getElementById('searchInput');
if (searchInput) {
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            filterJobs();
        }
    });
}

const locationInput = document.getElementById('locationInput');
if (locationInput) {
    locationInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            filterJobs();
        }
    });
}

// Real-time search (optional - uncomment to enable)
// let searchTimeout;
// searchInput?.addEventListener('input', function() {
//     clearTimeout(searchTimeout);
//     searchTimeout setTimeout(filterJobs, 300);
// });

