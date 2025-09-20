/**
 * Sine Wave Animation for Background
 * Creates dynamic, flowing sine waves with purple gradients
 */

class SineWaveRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        
        // Wave properties
        this.waves = [
            { amplitude: 80, frequency: 0.02, phase: 0, speed: 0.01, color: 'rgba(99, 102, 241, 0.4)' },
            { amplitude: 60, frequency: 0.025, phase: Math.PI / 3, speed: 0.015, color: 'rgba(139, 92, 246, 0.3)' },
            { amplitude: 100, frequency: 0.015, phase: Math.PI / 2, speed: 0.008, color: 'rgba(168, 85, 247, 0.2)' },
            { amplitude: 40, frequency: 0.03, phase: Math.PI, speed: 0.02, color: 'rgba(192, 132, 252, 0.5)' }
        ];
        
        this.time = 0;
        this.animationId = null;
        
        this.init();
    }
    
    init() {
        this.resize();
        this.animate();
        
        // Handle resize
        window.addEventListener('resize', () => this.resize());
    }
    
    resize() {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.canvas.width = this.width;
        this.canvas.height = this.height;
    }
    
    drawWave(wave, yOffset) {
        this.ctx.beginPath();
        this.ctx.strokeStyle = wave.color;
        this.ctx.lineWidth = 2;
        this.ctx.globalCompositeOperation = 'screen';
        
        // Create gradient for the wave
        const gradient = this.ctx.createLinearGradient(0, 0, this.width, 0);
        gradient.addColorStop(0, wave.color);
        gradient.addColorStop(0.5, wave.color.replace(/[\d\.]+\)$/g, '0.8)'));
        gradient.addColorStop(1, wave.color);
        
        this.ctx.strokeStyle = gradient;
        
        // Draw the sine wave
        for (let x = 0; x <= this.width; x++) {
            const y = yOffset + 
                     wave.amplitude * Math.sin(wave.frequency * x + wave.phase + this.time * wave.speed) +
                     20 * Math.sin(wave.frequency * 2 * x + wave.phase * 2 + this.time * wave.speed * 1.5);
            
            if (x === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }
        
        this.ctx.stroke();
        
        // Add flowing particles along the wave
        this.drawFlowingParticles(wave, yOffset);
    }
    
    drawFlowingParticles(wave, yOffset) {
        this.ctx.globalCompositeOperation = 'lighten';
        
        for (let i = 0; i < 5; i++) {
            const x = (this.time * wave.speed * 50 + i * 200) % (this.width + 100);
            const y = yOffset + 
                     wave.amplitude * Math.sin(wave.frequency * x + wave.phase + this.time * wave.speed) +
                     20 * Math.sin(wave.frequency * 2 * x + wave.phase * 2 + this.time * wave.speed * 1.5);
            
            // Create particle glow
            const particleGradient = this.ctx.createRadialGradient(x, y, 0, x, y, 15);
            particleGradient.addColorStop(0, wave.color.replace(/[\d\.]+\)$/g, '0.8)'));
            particleGradient.addColorStop(0.5, wave.color.replace(/[\d\.]+\)$/g, '0.4)'));
            particleGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
            
            this.ctx.fillStyle = particleGradient;
            this.ctx.beginPath();
            this.ctx.arc(x, y, 15, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Add smaller core particle
            this.ctx.fillStyle = wave.color.replace(/[\d\.]+\)$/g, '1)');
            this.ctx.beginPath();
            this.ctx.arc(x, y, 2, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
    
    drawInteractiveElements() {
        // Mouse-responsive wave distortion
        if (window.mouseX && window.mouseY) {
            const distanceFromMouse = Math.sqrt(
                Math.pow(window.mouseX - this.width / 2, 2) + 
                Math.pow(window.mouseY - this.height / 2, 2)
            );
            
            const influence = Math.max(0, 1 - distanceFromMouse / 300);
            
            if (influence > 0) {
                this.ctx.globalCompositeOperation = 'screen';
                const rippleGradient = this.ctx.createRadialGradient(
                    window.mouseX, window.mouseY, 0,
                    window.mouseX, window.mouseY, 150 * influence
                );
                rippleGradient.addColorStop(0, `rgba(99, 102, 241, ${0.3 * influence})`);
                rippleGradient.addColorStop(0.5, `rgba(139, 92, 246, ${0.2 * influence})`);
                rippleGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
                
                this.ctx.fillStyle = rippleGradient;
                this.ctx.beginPath();
                this.ctx.arc(window.mouseX, window.mouseY, 150 * influence, 0, Math.PI * 2);
                this.ctx.fill();
            }
        }
    }
    
    drawConnectionNodes() {
        // Draw connecting nodes that pulse with the waves
        const nodeCount = 8;
        this.ctx.globalCompositeOperation = 'screen';
        
        for (let i = 0; i < nodeCount; i++) {
            const x = (this.width / nodeCount) * i + (this.width / nodeCount) / 2;
            const baseY = this.height * 0.6;
            
            // Calculate Y position based on multiple wave influences
            let y = baseY;
            this.waves.forEach((wave, index) => {
                const influence = 0.3 + 0.1 * index;
                y += influence * wave.amplitude * Math.sin(
                    wave.frequency * x * 2 + wave.phase + this.time * wave.speed * 2
                );
            });
            
            // Draw connection lines between nodes
            if (i > 0) {
                const prevX = (this.width / nodeCount) * (i - 1) + (this.width / nodeCount) / 2;
                let prevY = baseY;
                this.waves.forEach((wave, index) => {
                    const influence = 0.3 + 0.1 * index;
                    prevY += influence * wave.amplitude * Math.sin(
                        wave.frequency * prevX * 2 + wave.phase + this.time * wave.speed * 2
                    );
                });
                
                const gradient = this.ctx.createLinearGradient(prevX, prevY, x, y);
                gradient.addColorStop(0, 'rgba(99, 102, 241, 0.4)');
                gradient.addColorStop(1, 'rgba(168, 85, 247, 0.4)');
                
                this.ctx.strokeStyle = gradient;
                this.ctx.lineWidth = 1;
                this.ctx.beginPath();
                this.ctx.moveTo(prevX, prevY);
                this.ctx.lineTo(x, y);
                this.ctx.stroke();
            }
            
            // Draw pulsing node
            const pulseSize = 3 + 2 * Math.sin(this.time * 0.05 + i * 0.5);
            const nodeGradient = this.ctx.createRadialGradient(x, y, 0, x, y, pulseSize * 3);
            nodeGradient.addColorStop(0, 'rgba(192, 132, 252, 0.8)');
            nodeGradient.addColorStop(0.5, 'rgba(139, 92, 246, 0.4)');
            nodeGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
            
            this.ctx.fillStyle = nodeGradient;
            this.ctx.beginPath();
            this.ctx.arc(x, y, pulseSize * 3, 0, Math.PI * 2);
            this.ctx.fill();
            
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            this.ctx.beginPath();
            this.ctx.arc(x, y, pulseSize, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        this.ctx.globalCompositeOperation = 'source-over';
        
        // Draw background gradient
        const bgGradient = this.ctx.createLinearGradient(0, 0, this.width, this.height);
        bgGradient.addColorStop(0, 'rgba(15, 15, 35, 0.1)');
        bgGradient.addColorStop(0.5, 'rgba(26, 26, 58, 0.05)');
        bgGradient.addColorStop(1, 'rgba(15, 15, 35, 0.1)');
        
        this.ctx.fillStyle = bgGradient;
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // Draw waves at different vertical positions
        this.waves.forEach((wave, index) => {
            const yOffset = this.height * (0.3 + 0.15 * index);
            this.drawWave(wave, yOffset);
        });
        
        // Draw connection nodes
        this.drawConnectionNodes();
        
        // Draw interactive elements
        this.drawInteractiveElements();
        
        // Update time for animation
        this.time += 1;
        
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        window.removeEventListener('resize', this.resize);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('waveCanvas');
    if (canvas) {
        const waveRenderer = new SineWaveRenderer(canvas);
        
        // Track mouse position for interactive effects
        document.addEventListener('mousemove', (e) => {
            window.mouseX = e.clientX;
            window.mouseY = e.clientY;
        });
        
        // Clean up on page unload
        window.addEventListener('beforeunload', () => {
            waveRenderer.destroy();
        });
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SineWaveRenderer;
}