// JavaScript to create modern floating polyhedron-like shapes in monochromatic tones
document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('floating-agents-container') || document.createElement('div');
    if (!container.id) {
        container.id = 'floating-agents-container';
        document.body.appendChild(container);
    }

    const shapesCount = 20;
    const shapes = [];

    for (let i = 0; i < shapesCount; i++) {
        const shape = document.createElement('div');
        shape.className = 'floating-shape';

        // Random position
        shape.style.left = Math.random() * 100 + 'vw';
        shape.style.top = Math.random() * 100 + 'vh';

        // Random size
        const size = 20 + Math.random() * 40;
        shape.style.width = size + 'px';
        shape.style.height = size + 'px';

        // Random animation duration
        shape.style.animationDuration = 6 + Math.random() * 8 + 's';

        // Random delay
        shape.style.animationDelay = Math.random() * 5 + 's';

        // Random polygon shape using clip-path
        const polygons = [
            'polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%)', // pentagon
            'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)', // hexagon
            'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)', // diamond
            'polygon(50% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)', // irregular pentagon
            'polygon(50% 0%, 100% 38%, 100% 62%, 50% 100%, 0% 62%, 0% 38%)', // hexagon variant
            'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)' // octagon
        ];
        shape.style.clipPath = polygons[Math.floor(Math.random() * polygons.length)];

        // Random grayscale color with slight blue tint for modernity
        const grayScale = Math.floor(Math.random() * 156) + 100; // 100 to 255
        const blueBoost = Math.min(255, grayScale + Math.floor(Math.random() * 20)); // Slight blue tint
        
        // Randomly choose between pure grayscale and blue-tinted grayscale
        if (Math.random() > 0.7) {
            shape.style.backgroundColor = `rgb(${grayScale}, ${grayScale}, ${blueBoost})`;
        } else {
            shape.style.backgroundColor = `rgb(${grayScale}, ${grayScale}, ${grayScale})`;
        }

        // Add subtle border for depth
        if (Math.random() > 0.5) {
            shape.style.border = '1px solid rgba(255,255,255,0.1)';
        }

        container.appendChild(shape);
        shapes.push(shape);
    }

    // Add occasional interaction - shapes react to mouse movement
    document.addEventListener('mousemove', function(e) {
        const mouseX = e.clientX;
        const mouseY = e.clientY;
        
        shapes.forEach((shape, index) => {
            if (index % 3 === 0) { // Only affect every third shape for performance
                const rect = shape.getBoundingClientRect();
                const shapeX = rect.left + rect.width/2;
                const shapeY = rect.top + rect.height/2;
                
                const distX = mouseX - shapeX;
                const distY = mouseY - shapeY;
                const distance = Math.sqrt(distX * distX + distY * distY);
                
                if (distance < 200) {
                    const angle = Math.atan2(distY, distX);
                    const push = 1 - (distance / 200);
                    
                    // Subtle repulsion effect
                    shape.style.transform = `translate(${-Math.cos(angle) * push * 10}px, ${-Math.sin(angle) * push * 10}px)`;
                } else {
                    shape.style.transform = '';
                }
            }
        });
    });
});
