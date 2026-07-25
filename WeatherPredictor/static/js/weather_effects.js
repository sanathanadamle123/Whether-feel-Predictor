/**
 * WeatherPredictor Animated Canvas Weather Background Effects
 */

class WeatherEffects {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.effect = 'sunny'; // Default effect
        this.animationId = null;
        
        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.initParticles();
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    setEffect(effect) {
        if (this.effect === effect) return;
        this.effect = effect;
        this.initParticles();
    }

    initParticles() {
        this.particles = [];
        const count = this.getParticleCount();

        for (let i = 0; i < count; i++) {
            this.particles.push(this.createParticle());
        }
    }

    getParticleCount() {
        switch (this.effect) {
            case 'snow': return 120;
            case 'rain': return 180;
            case 'clouds': return 8;
            case 'sunny': return 4;
            case 'heatwave': return 35;
            default: return 20;
        }
    }

    createParticle() {
        const w = this.canvas.width;
        const h = this.canvas.height;

        if (this.effect === 'snow') {
            return {
                x: Math.random() * w,
                y: Math.random() * h,
                radius: Math.random() * 3 + 1,
                speedY: Math.random() * 1.5 + 0.5,
                speedX: Math.random() * 0.8 - 0.4,
                opacity: Math.random() * 0.7 + 0.3
            };
        } else if (this.effect === 'rain') {
            return {
                x: Math.random() * w,
                y: Math.random() * h,
                length: Math.random() * 20 + 10,
                speedY: Math.random() * 12 + 8,
                speedX: -2,
                opacity: Math.random() * 0.5 + 0.3
            };
        } else if (this.effect === 'clouds') {
            return {
                x: Math.random() * w,
                y: Math.random() * (h * 0.5),
                radius: Math.random() * 80 + 60,
                speedX: Math.random() * 0.3 + 0.1,
                opacity: Math.random() * 0.12 + 0.05
            };
        } else if (this.effect === 'sunny') {
            return {
                x: w * 0.8,
                y: h * 0.2,
                radius: Math.random() * 200 + 150,
                pulse: Math.random() * 0.02 + 0.01,
                alpha: 0.15
            };
        } else if (this.effect === 'heatwave') {
            return {
                x: Math.random() * w,
                y: h + Math.random() * 50,
                radius: Math.random() * 6 + 2,
                speedY: -(Math.random() * 2 + 1),
                opacity: Math.random() * 0.4 + 0.1,
                wobble: Math.random() * 0.05
            };
        }
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.particles.forEach((p, idx) => {
            this.ctx.beginPath();

            if (this.effect === 'snow') {
                this.ctx.fillStyle = `rgba(255, 255, 255, ${p.opacity})`;
                this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                this.ctx.fill();

                p.y += p.speedY;
                p.x += p.speedX;
                if (p.y > this.canvas.height) { p.y = -10; p.x = Math.random() * this.canvas.width; }

            } else if (this.effect === 'rain') {
                this.ctx.strokeStyle = `rgba(56, 189, 248, ${p.opacity})`;
                this.ctx.lineWidth = 1.5;
                this.ctx.moveTo(p.x, p.y);
                this.ctx.lineTo(p.x + p.speedX, p.y + p.length);
                this.ctx.stroke();

                p.y += p.speedY;
                p.x += p.speedX;
                if (p.y > this.canvas.height) { p.y = -20; p.x = Math.random() * this.canvas.width; }

            } else if (this.effect === 'clouds') {
                const grad = this.ctx.createRadialGradient(p.x, p.y, 10, p.x, p.y, p.radius);
                grad.addColorStop(0, `rgba(255, 255, 255, ${p.opacity})`);
                grad.addColorStop(1, 'rgba(255, 255, 255, 0)');

                this.ctx.fillStyle = grad;
                this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                this.ctx.fill();

                p.x += p.speedX;
                if (p.x - p.radius > this.canvas.width) p.x = -p.radius;

            } else if (this.effect === 'sunny') {
                const grad = this.ctx.createRadialGradient(p.x, p.y, 20, p.x, p.y, p.radius);
                grad.addColorStop(0, 'rgba(251, 191, 36, 0.25)');
                grad.addColorStop(0.5, 'rgba(245, 158, 11, 0.08)');
                grad.addColorStop(1, 'rgba(255, 255, 255, 0)');

                this.ctx.fillStyle = grad;
                this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                this.ctx.fill();

            } else if (this.effect === 'heatwave') {
                this.ctx.fillStyle = `rgba(248, 113, 113, ${p.opacity})`;
                this.ctx.arc(p.x + Math.sin(p.y * p.wobble) * 8, p.y, p.radius, 0, Math.PI * 2);
                this.ctx.fill();

                p.y += p.speedY;
                if (p.y < -20) { p.y = this.canvas.height + 20; p.x = Math.random() * this.canvas.width; }
            }
        });
    }

    animate() {
        this.draw();
        this.animationId = requestAnimationFrame(() => this.animate());
    }
}

// Global initialization when DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.weatherEffects = new WeatherEffects('weather-canvas');
});
