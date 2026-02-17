/**
 * CV Builder - Client-side JavaScript
 * Handles form submission, section management, and live preview
 */

class CVBuilder {
    constructor(cvId, csrfToken) {
        this.cvId = cvId;
        this.csrfToken = csrfToken;
        this.previewRefreshTimeout = null;
        this.saveTimeout = null;
        this.init();
    }

    init() {
        // Attach event listeners
        this.attachFormListeners();
        this.loadSections();
    }

    attachFormListeners() {
        const form = document.getElementById('cvForm');
        if (!form) return;

        // Auto-save and preview refresh on input
        form.addEventListener('input', (e) => {
            this.onFormChange();
        });

        // Prevent form submission
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveCV();
        });
    }

    onFormChange() {
        // Update save status
        this.updateSaveStatus('unsaved');

        // Debounced preview refresh
        clearTimeout(this.previewRefreshTimeout);
        this.previewRefreshTimeout = setTimeout(() => {
            this.refreshPreview();
        }, 1000);

        // Debounced auto-save
        clearTimeout(this.saveTimeout);
        this.saveTimeout = setTimeout(() => {
            this.autoSave();
        }, 3000);
    }

    updateSaveStatus(status) {
        const indicator = document.getElementById('saveStatus');
        if (!indicator) return;

        const states = {
            'saved': {
                text: 'All changes saved',
                bg: '#e8f0fe',
                color: '#1967d2'
            },
            'unsaved': {
                text: 'Unsaved changes',
                bg: '#fce8e6',
                color: '#c5221f'
            },
            'saving': {
                text: 'Saving...',
                bg: '#fef7e0',
                color: '#f9ab00'
            }
        };

        const state = states[status] || states.unsaved;
        indicator.textContent = state.text;
        indicator.style.background = state.bg;
        indicator.style.color = state.color;
    }

    refreshPreview() {
        const iframe = document.getElementById('previewFrame');
        if (iframe) {
            iframe.src = `/cv/${this.cvId}/preview?t=${Date.now()}`;
        }
    }

    async loadSections() {
        try {
            const response = await fetch(`/cv/api/${this.cvId}/sections`, {
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) throw new Error('Failed to load sections');

            const data = await response.json();
            console.log('Loaded sections:', data.sections);
        } catch (error) {
            console.error('Error loading sections:', error);
        }
    }

    async saveCV() {
        this.updateSaveStatus('saving');

        try {
            const formData = this.collectFormData();
            await this.saveSections(formData);

            this.updateSaveStatus('saved');
            this.refreshPreview();
        } catch (error) {
            console.error('Save failed:', error);
            alert('Failed to save CV. Please try again.');
            this.updateSaveStatus('unsaved');
        }
    }

    async autoSave() {
        console.log('Auto-saving...');
        const formData = this.collectFormData();
        await this.saveSections(formData);
        this.updateSaveStatus('saved');
    }

    collectFormData() {
        const form = document.getElementById('cvForm');
        const data = {
            personal: {},
            summary: '',
            experience: [],
            education: [],
            skills: {}
        };

        // Personal info
        const personalFields = form.querySelectorAll('[name^="personal."]');
        personalFields.forEach(field => {
            const key = field.name.replace('personal.', '');
            data.personal[key] = field.value;
        });

        // Summary
        const summaryField = form.querySelector('[name="summary"]');
        if (summaryField) {
            data.summary = summaryField.value;
        }

        // Skills
        const skillFields = form.querySelectorAll('[name^="skills."]');
        skillFields.forEach(field => {
            const key = field.name.replace('skills.', '');
            data.skills[key] = field.value;
        });

        // Experience entries
        const expEntries = form.querySelectorAll('[data-section-id][name^="exp_"]');
        const expBySectionId = {};

        expEntries.forEach(field => {
            const sectionId = field.dataset.sectionId;
            if (!expBySectionId[sectionId]) {
                expBySectionId[sectionId] = { id: sectionId };
            }

            const fieldName = field.name.replace('exp_', '');
            expBySectionId[sectionId][fieldName] = field.value;
        });

        data.experience = Object.values(expBySectionId);

        // Education entries
        const eduEntries = form.querySelectorAll('[data-section-id][name^="edu_"]');
        const eduBySectionId = {};

        eduEntries.forEach(field => {
            const sectionId = field.dataset.sectionId;
            if (!eduBySectionId[sectionId]) {
                eduBySectionId[sectionId] = { id: sectionId };
            }

            const fieldName = field.name.replace('edu_', '');
            eduBySectionId[sectionId][fieldName] = field.value;
        });

        data.education = Object.values(eduBySectionId);

        return data;
    }

    async saveSections(data) {
        // Save personal info
        if (data.personal && Object.keys(data.personal).length > 0) {
            await this.updateOrCreateSection('personal', {
                content: data.personal
            });
        }

        // Save summary
        if (data.summary) {
            await this.updateOrCreateSection('summary', {
                content: { text: data.summary }
            });
        }

        // Save skills
        if (data.skills && Object.keys(data.skills).length > 0) {
            await this.updateOrCreateSection('skills', {
                content: data.skills
            });
        }

        // Save experience entries
        for (const exp of data.experience) {
            if (exp.id && exp.id !== 'new') {
                await this.updateSection(exp.id, {
                    content: {
                        title: exp.title,
                        company: exp.company,
                        start_date: exp.start,
                        end_date: exp.end,
                        location: exp.location,
                        description: exp.description
                    }
                });
            }
        }

        // Save education entries
        for (const edu of data.education) {
            if (edu.id && edu.id !== 'new') {
                await this.updateSection(edu.id, {
                    content: {
                        degree: edu.degree,
                        field: edu.field,
                        institution: edu.institution,
                        year: edu.year,
                        gpa: edu.gpa
                    }
                });
            }
        }
    }

    async updateOrCreateSection(type, data) {
        // Try to find existing section
        const sections = await this.getSections();
        const existing = sections.find(s => s.section_type === type);

        if (existing) {
            return await this.updateSection(existing.id, data);
        } else {
            return await this.createSection(type, data);
        }
    }

    async getSections() {
        try {
            const response = await fetch(`/cv/api/${this.cvId}/sections`, {
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) throw new Error('Failed to get sections');

            const data = await response.json();
            return data.sections;
        } catch (error) {
            console.error('Error getting sections:', error);
            return [];
        }
    }

    async createSection(type, data) {
        const response = await fetch(`/cv/api/${this.cvId}/sections`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            },
            body: JSON.stringify({
                section_type: type,
                ...data
            })
        });

        if (!response.ok) throw new Error(`Failed to create ${type} section`);

        return await response.json();
    }

    async updateSection(sectionId, data) {
        const response = await fetch(`/cv/api/${this.cvId}/sections/${sectionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error(`Failed to update section ${sectionId}`);

        return await response.json();
    }

    async deleteSection(sectionId) {
        const response = await fetch(`/cv/api/${this.cvId}/sections/${sectionId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': this.csrfToken
            }
        });

        if (!response.ok) throw new Error(`Failed to delete section ${sectionId}`);

        return await response.json();
    }

    async addExperience() {
        const container = document.getElementById('experienceEntries');
        if (!container) return;

        // Create new experience entry
        const result = await this.createSection('experience', {
            content: {
                title: '',
                company: '',
                start_date: '',
                end_date: 'Present',
                location: '',
                description: ''
            },
            display_order: 999
        });

        if (result.success) {
            // Reload page to show new entry
            window.location.reload();
        }
    }

    async addEducation() {
        const result = await this.createSection('education', {
            content: {
                degree: '',
                field: '',
                institution: '',
                year: '',
                gpa: ''
            },
            display_order: 999
        });

        if (result.success) {
            window.location.reload();
        }
    }
}

// Initialize builder when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (typeof CV_ID !== 'undefined' && typeof CSRF_TOKEN !== 'undefined') {
        window.cvBuilder = new CVBuilder(CV_ID, CSRF_TOKEN);
    }
});

// Global functions for template buttons
function addExperience() {
    if (window.cvBuilder) {
        window.cvBuilder.addExperience();
    }
}

function addEducation() {
    if (window.cvBuilder) {
        window.cvBuilder.addEducation();
    }
}

function addOrUpdateSection(type) {
    if (window.cvBuilder) {
        window.cvBuilder.saveCV();
    }
}

function deleteSection(id) {
    if (!window.cvBuilder) return;

    if (confirm('Delete this entry?')) {
        window.cvBuilder.deleteSection(id).then(() => {
            window.location.reload();
        }).catch(error => {
            alert('Failed to delete: ' + error.message);
        });
    }
}

function saveCV() {
    if (window.cvBuilder) {
        window.cvBuilder.saveCV();
    }
}
