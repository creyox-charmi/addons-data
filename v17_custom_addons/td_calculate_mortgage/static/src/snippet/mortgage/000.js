/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.mortgageFormWizard = publicWidget.Widget.extend({
    selector: '#mainForm',
    disabledInEditableMode: false,

    start() {
        this.sections = Array.from(this.el.querySelectorAll('.form-section'));
        this.nextBtn = this.el.querySelector('#nextBtn');
        this.prevBtn = this.el.querySelector('#prevBtn');
        this.submitBtn = this.el.querySelector('#submitBtn');
        this.progressBar = document.querySelector('#progressBar');
        this.currentSection = 0;
        this.titularCount = 0;

        this._initDefaults();
        this._bindEvents();
        this._updateSection();
        return this._super(...arguments);
    },

    _initDefaults() {
        // Mark radios and inputs as required
        const requiredSelectors = [
            'input[name="estado_busqueda"]',
            'input[name="tipo_hipoteca"]',
            'input[name="titular"]',
            'input[name="nivel_ingresos_titular_1"]',
            'input[name="total_prestamos_titular_1"]',
            '#option2-1', '#option2-2',
            '#option3-1', '#option3-2',
            '#option3-3', '#option3-4'
        ];
        requiredSelectors.forEach(sel => {
            this.el.querySelectorAll(sel).forEach(el => el.required = true);
        });

        // Sliders default
        const range2 = this.el.querySelector('#option2-2');
        const output2 = this.el.querySelector('#option2-1');
        if (range2 && output2) {
            output2.readOnly = true;
            range2.value = 500000;
            output2.value = `€ ${(+range2.value).toLocaleString()}`;
            range2.addEventListener('input', () => {
                output2.value = `€ ${(+range2.value).toLocaleString()}`;
                this._validateCurrentSection();
            });
        }

        const rangeSaved = this.el.querySelector('#option3-2');
        const inputSaved = this.el.querySelector('#option3-1');
        if (rangeSaved && inputSaved) {
            inputSaved.readOnly = true;
            rangeSaved.value = 1;
            inputSaved.value = `€ ${(+rangeSaved.value).toLocaleString()}`;
            rangeSaved.addEventListener('input', () => {
                inputSaved.value = `€ ${(+rangeSaved.value).toLocaleString()}`;
                this._validateCurrentSection();
            });
        }

        const rangeYears = this.el.querySelector('#option3-4');
        const inputYears = this.el.querySelector('#option3-3');
        if (rangeYears && inputYears) {
            inputYears.readOnly = true;
            rangeYears.value = 20;
            inputYears.value = `${rangeYears.value}`;
            rangeYears.addEventListener('input', () => {
                inputYears.value = `${rangeYears.value}`;
                this._validateCurrentSection();
            });
        }
    },

    _bindEvents() {
        this.nextBtn.addEventListener('click', () => {
            if (!this._validateCurrentSection()) {
                alert('⚠ There was an error saving the data: Required data is missing.');
                return;
            }
            this.currentSection++;
            this._updateSection();
        });

        this.prevBtn.addEventListener('click', () => {
            this.currentSection = Math.max(0, this.currentSection - 1);
            this._updateSection();
        });

        const solo = this.el.querySelector('#option4-1');
        const duo = this.el.querySelector('#option4-2');
        const ds = this.el.querySelector('#titular_dos_oculta');
        const dd = this.el.querySelector('#titular');

        if (solo && duo && ds && dd) {
            ds.style.display = 'none';
            dd.style.display = 'none';
            ds.querySelectorAll('input').forEach(i => { i.disabled = true; i.required = false; });
            dd.querySelectorAll('input').forEach(i => { i.disabled = true; i.required = false; });

            const onHolder = () => {
                if (solo.checked) {
                    ds.style.display = 'block';
                    dd.style.display = 'none';
                    this.titularCount = 1;
                    ds.querySelectorAll('input').forEach(i => { i.disabled = false; i.required = true; });
                    dd.querySelectorAll('input').forEach(i => { i.disabled = true;  i.required = false; });
                    this.el.querySelectorAll('input[name="total_prestamos_titular_2"]').forEach(i => {
                        i.disabled = true;
                        i.required = false;
                    });
                } else if (duo.checked) {
                    ds.style.display = 'none';
                    dd.style.display = 'block';
                    this.titularCount = 2;
                    dd.querySelectorAll('input').forEach(i => { i.disabled = false; i.required = true; });
                    ds.querySelectorAll('input').forEach(i => { i.disabled = true;  i.required = false; });
                    this.el.querySelectorAll('input[name="total_prestamos_titular_2"]').forEach(i => {
                        i.disabled = false;
                        i.required = true;
                    });
                }
                if (this._isSectionValid()) {
                    this.currentSection++;
                    this._updateSection();
                } else {
                    alert('Please select an option.');
                }
            };

            solo.addEventListener('change', onHolder);
            duo.addEventListener('change', onHolder);
        }

        this.sections.forEach(sec => {
            sec.querySelectorAll('input,select').forEach(f => {
                f.addEventListener('input', () => this._validateCurrentSection());
                f.addEventListener('change', () => this._validateCurrentSection());
            });
        });

        this.el.addEventListener('submit', e => {
            e.preventDefault();
            if (!this._isSectionValid()) {
                alert('⚠ There was an error saving the data: Required data is missing.');
                return;
            }
            const fd = new FormData(this.el), data = {};
            fd.forEach((v, k) => data[k] = v);
            fetch('/mortgage/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(res => {
                if (res.ok) {
                    window.location.href = '/contactus-thank-you';
                } else {
                    alert('❌ Submission failed.');
                }
            }).catch(() => {
                alert('⚠ There was an error saving the data: Required data is missing.');
            });
        });
    },

    _updateSection() {
    console.log('yes update')
        this.sections.forEach((sec, i) => sec.classList.toggle('active', i === this.currentSection));
        this.prevBtn.style.display = this.currentSection > 0 ? 'inline-block' : 'none';
        this.nextBtn.style.display = this.currentSection < this.sections.length - 2 ? 'inline-block' : 'none';
        this.submitBtn.style.display = this.currentSection === this.sections.length - 2 ? 'inline-block' : 'none';
        console.log('this.progressBar ',this.progressBar)
        if (this.progressBar) {
            console.log('in progres..')
            this.progressBar.style.width = `${(this.currentSection / (this.sections.length - 2)) * 100}%`;
        }

        const prestamos = this.el.querySelector('#prestamos');
        if (prestamos) {
            prestamos.style.display = this.currentSection === 6 && this.titularCount === 2 ? 'block' : 'none';
        }

        this._validateCurrentSection();
    },

    _isSectionValid() {
        const sec = this.sections[this.currentSection];
        const required = sec.querySelectorAll('input[required], select[required]');
        const seen = new Set();
        let valid = true;

        required.forEach(input => {
            if (input.disabled || input.offsetParent === null) return;
            if (input.type === 'radio' || input.type === 'checkbox') {
                if (!seen.has(input.name)) {
                    if (!sec.querySelector(`input[name="${input.name}"]:checked`)) valid = false;
                    seen.add(input.name);
                }
            } else {
                if (input.name === 'telefono') {
                    const phoneValid = /^[6789][0-9]{8}$/.test(input.value.trim());
                    if (!phoneValid) valid = false;
                } else if (!input.value.trim()) {
                    valid = false;
                }
            }
        });

        return valid;
    },

    _validateCurrentSection() {
        this.nextBtn.disabled = !this._isSectionValid();
        return !this.nextBtn.disabled;
    },
});

