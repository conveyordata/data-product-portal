import { motion, useMotionValue, useReducedMotion, useSpring, useTransform } from 'framer-motion';
import { type MouseEvent, useRef, useState } from 'react';

export default function AnimatedWizard({ size = 350, robeColor = '#1e1b4b', magicColor = '#3b82f6' }) {
    const containerRef = useRef<HTMLDivElement | null>(null);
    const [isCasting, setIsCasting] = useState(false);
    const prefersReducedMotion = useReducedMotion();

    // --- MOUSE TRACKING ---
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    const smoothX = useSpring(mouseX, { damping: 20, stiffness: 100 });
    const smoothY = useSpring(mouseY, { damping: 20, stiffness: 100 });

    const tiltMultiplier = prefersReducedMotion ? 0 : 1;
    const rotateX = useTransform(smoothY, [-150, 150], [10 * tiltMultiplier, -10 * tiltMultiplier]);
    const rotateY = useTransform(smoothX, [-150, 150], [-10 * tiltMultiplier, 10 * tiltMultiplier]);

    const robeX = useTransform(smoothX, [-150, 150], [-1, 1]);
    const robeY = useTransform(smoothY, [-150, 150], [-1, 1]);
    const headX = useTransform(smoothX, [-150, 150], [-3, 3]);
    const headY = useTransform(smoothY, [-150, 150], [-3, 3]);
    const orbX = useTransform(smoothX, [-150, 150], [-8, 8]);
    const orbY = useTransform(smoothY, [-150, 150], [-6, 6]);

    const handleMouseMove = (event: MouseEvent) => {
        if (!containerRef.current || prefersReducedMotion) return;
        const rect = containerRef.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        mouseX.set(event.clientX - centerX);
        mouseY.set(event.clientY - centerY);
    };

    const handleMouseLeave = () => {
        mouseX.set(0);
        mouseY.set(0);
    };

    const handleTap = () => {
        if (isCasting) return;
        setIsCasting(true);
        setTimeout(() => setIsCasting(false), 800);
    };

    const ORB_CENTER_X = 175;
    const ORB_CENTER_Y = 110;

    // FIX 1: The Centering Wrapper
    return (
        <div className="w-full h-full flex items-center justify-center overflow-visible">
            <div
                ref={containerRef}
                onMouseMove={handleMouseMove}
                onMouseLeave={handleMouseLeave}
                onClick={handleTap}
                style={{ width: size, height: size, flexShrink: 0, perspective: 1000 }}
                role="spinbutton"
                tabIndex={0}
                aria-label="Animated Wizard Mascot"
                className="relative flex items-center justify-center cursor-pointer overflow-visible outline-none focus-visible:ring-4 focus-visible:ring-blue-500 rounded-full transition-all"
            >
                <motion.div style={{ rotateX, rotateY, transformStyle: 'preserve-3d' }} className="w-full h-full">
                    <motion.svg
                        viewBox="-30 -40 300 300"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                        className="w-full h-full overflow-visible drop-shadow-2xl"
                    >
                        <defs>
                            <pattern id="starPattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                                <circle cx="4" cy="4" r="0.5" fill="#ffffff" opacity="0.6" />
                                <circle cx="16" cy="14" r="0.8" fill="#fbbf24" opacity="0.8" />
                                <path
                                    d="M10 5 L11 9 L15 10 L11 11 L10 15 L9 11 L5 10 L9 9 Z"
                                    fill="#fbbf24"
                                    opacity="0.7"
                                    transform="scale(0.5) translate(10, -5)"
                                />
                            </pattern>
                            <linearGradient id="robeShading" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stopColor="#000000" stopOpacity="0.5" />
                                <stop offset="50%" stopColor="#ffffff" stopOpacity="0.1" />
                                <stop offset="100%" stopColor="#000000" stopOpacity="0.7" />
                            </linearGradient>
                            <radialGradient id="orbGlow" cx="50%" cy="50%" r="50%">
                                <stop offset="0%" stopColor="#ffffff" stopOpacity="1" />
                                <stop offset="30%" stopColor={magicColor} stopOpacity="0.9" />
                                <stop offset="100%" stopColor={magicColor} stopOpacity="0" />
                            </radialGradient>
                            <radialGradient id="faceLighting" cx="80%" cy="50%" r="50%">
                                <stop offset="0%" stopColor={magicColor} stopOpacity="0.3" />
                                <stop offset="100%" stopColor={magicColor} stopOpacity="0" />
                            </radialGradient>

                            {/* FIX 2: Ambient Backlight Gradient */}
                            <radialGradient id="ambientBacklight" cx="50%" cy="50%" r="50%">
                                <stop offset="0%" stopColor={magicColor} stopOpacity="0.25" />
                                <stop offset="50%" stopColor={magicColor} stopOpacity="0.1" />
                                <stop offset="100%" stopColor={magicColor} stopOpacity="0" />
                            </radialGradient>

                            <filter id="dropShadow" x="-50%" y="-50%" width="200%" height="200%">
                                <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#000" floodOpacity="0.4" />
                            </filter>
                        </defs>

                        {/* FIX 2: Ambient Backlight Sphere (Placed at the very back) */}
                        <motion.circle
                            cx="120"
                            cy="110"
                            r="130"
                            fill="url(#ambientBacklight)"
                            animate={{
                                scale: isCasting ? 1.3 : [1, 1.05, 1],
                                opacity: isCasting ? 0.6 : [0.5, 0.8, 0.5],
                            }}
                            transition={{
                                duration: isCasting ? 0.3 : 4,
                                repeat: isCasting ? 0 : Number.POSITIVE_INFINITY,
                                ease: 'easeInOut',
                            }}
                        />

                        {/* GROUND SHADOW */}
                        <motion.ellipse
                            cx="120"
                            cy="210"
                            rx="45"
                            ry="12"
                            fill="#000000"
                            opacity="0.2"
                            filter="blur(4px)"
                            animate={prefersReducedMotion ? {} : { scale: [1, 1.15, 1], opacity: [0.2, 0.1, 0.2] }}
                            transition={{ duration: 3.5, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
                        />

                        {/* INTERACTIVE GROUP: The jump */}
                        <motion.g
                            animate={{ y: isCasting ? -20 : 0 }}
                            transition={{ type: 'spring', stiffness: 400, damping: 15 }}
                        >
                            {/* IDLE GROUP: The float */}
                            <motion.g
                                animate={prefersReducedMotion ? {} : { y: [0, -12, 0] }}
                                transition={{ duration: 3.5, repeat: Number.POSITIVE_INFINITY, ease: 'easeInOut' }}
                            >
                                {/* LAYER 1: The Robe */}
                                <motion.g style={{ x: robeX, y: robeY }}>
                                    <path d="M60 190 L110 70 L170 190 Q115 205 60 190 Z" fill={robeColor} />
                                    <path d="M60 190 L110 70 L170 190 Q115 205 60 190 Z" fill="url(#starPattern)" />
                                    <path d="M60 190 L110 70 L170 190 Q115 205 60 190 Z" fill="url(#robeShading)" />
                                </motion.g>

                                {/* LAYER 2: Head, Hat & Beard */}
                                <motion.g style={{ x: headX, y: headY }}>
                                    <circle cx="120" cy="85" r="22" fill="#fed7aa" filter="url(#dropShadow)" />
                                    <motion.circle
                                        cx="120"
                                        cy="85"
                                        r="22"
                                        fill="url(#faceLighting)"
                                        animate={{ opacity: isCasting ? 1 : 0.6 }}
                                        transition={{ duration: 0.3 }}
                                    />

                                    <circle cx="106" cy="94" r="4" fill="#f87171" opacity="0.4" />
                                    <circle cx="134" cy="94" r="4" fill="#f87171" opacity="0.4" />

                                    <motion.g
                                        animate={prefersReducedMotion ? {} : { scaleY: [1, 1, 0.1, 1, 1] }}
                                        transition={{
                                            duration: 4,
                                            repeat: Number.POSITIVE_INFINITY,
                                            times: [0, 0.9, 0.95, 0.98, 1],
                                        }}
                                        style={{ transformOrigin: '120px 92px' }}
                                    >
                                        <circle cx="112" cy="92" r="2.5" fill="#1e293b" />
                                        <circle cx="128" cy="92" r="2.5" fill="#1e293b" />
                                    </motion.g>

                                    <g filter="url(#dropShadow)">
                                        <path d="M85 75 L120 15 L155 75 Z" fill={robeColor} />
                                        <path d="M85 75 L120 15 L155 75 Z" fill="url(#starPattern)" />
                                        <path d="M85 75 L120 15 L155 75 Z" fill="url(#robeShading)" />
                                        <path
                                            d="M65 75 Q120 85 175 75"
                                            stroke={robeColor}
                                            strokeWidth="12"
                                            strokeLinecap="round"
                                        />
                                        <path
                                            d="M65 75 Q120 85 175 75"
                                            stroke="url(#starPattern)"
                                            strokeWidth="12"
                                            strokeLinecap="round"
                                        />
                                        <path
                                            d="M65 75 Q120 85 175 75"
                                            stroke="url(#robeShading)"
                                            strokeWidth="12"
                                            strokeLinecap="round"
                                        />
                                    </g>

                                    <path
                                        d="M98 95 Q120 150 142 95 Q120 102 98 95 Z"
                                        fill="#f8fafc"
                                        filter="url(#dropShadow)"
                                    />
                                    <path
                                        d="M98 95 Q120 150 142 95 Q120 102 98 95 Z"
                                        fill="url(#robeShading)"
                                        opacity="0.3"
                                    />
                                </motion.g>

                                {/* LAYER 3: The Magic Orb */}
                                <motion.g style={{ x: orbX, y: orbY }}>
                                    <motion.g
                                        animate={{ scale: isCasting ? 1.5 : 1 }}
                                        transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                                        style={{ originX: `${ORB_CENTER_X}px`, originY: `${ORB_CENTER_Y}px` }}
                                    >
                                        <motion.circle
                                            cx={ORB_CENTER_X}
                                            cy={ORB_CENTER_Y}
                                            r="30"
                                            fill="url(#orbGlow)"
                                            animate={{ opacity: [0.6, 1, 0.6], scale: [1, 1.05, 1] }}
                                            transition={{
                                                duration: 2,
                                                repeat: Number.POSITIVE_INFINITY,
                                                ease: 'easeInOut',
                                            }}
                                        />
                                        <circle cx={ORB_CENTER_X - 4} cy={ORB_CENTER_Y - 4} r="4" fill="#ffffff" />
                                    </motion.g>

                                    <motion.g
                                        animate={{ rotate: 360 }}
                                        transition={{ duration: 6, repeat: Number.POSITIVE_INFINITY, ease: 'linear' }}
                                        style={{ originX: `${ORB_CENTER_X}px`, originY: `${ORB_CENTER_Y}px` }}
                                    >
                                        <motion.path
                                            d="M200 90 L202 95 L207 97 L202 99 L200 104 L198 99 L193 97 L198 95 Z"
                                            fill="#ffffff"
                                            animate={{ scale: [0.5, 1, 0.5] }}
                                            transition={{ duration: 3, repeat: Number.POSITIVE_INFINITY }}
                                        />
                                        <motion.path
                                            d="M150 130 L151 133 L154 134 L151 135 L150 138 L149 135 L146 134 L149 133 Z"
                                            fill={magicColor}
                                            animate={{ scale: [1, 0.5, 1] }}
                                            transition={{ duration: 2.5, repeat: Number.POSITIVE_INFINITY }}
                                        />
                                    </motion.g>

                                    <motion.g
                                        animate={{ rotate: -360 }}
                                        transition={{ duration: 4, repeat: Number.POSITIVE_INFINITY, ease: 'linear' }}
                                        style={{ originX: `${ORB_CENTER_X}px`, originY: `${ORB_CENTER_Y}px` }}
                                    >
                                        <motion.circle
                                            cx={ORB_CENTER_X - 25}
                                            cy={ORB_CENTER_Y - 15}
                                            r="1.5"
                                            fill="#ffffff"
                                            animate={{ opacity: [0.2, 1, 0.2] }}
                                            transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY }}
                                        />
                                        <motion.circle
                                            cx={ORB_CENTER_X + 25}
                                            cy={ORB_CENTER_Y + 15}
                                            r="2"
                                            fill="#fbbf24"
                                            animate={{ opacity: [1, 0.4, 1] }}
                                            transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY }}
                                        />
                                    </motion.g>
                                </motion.g>
                            </motion.g>
                        </motion.g>
                    </motion.svg>
                </motion.div>
            </div>
        </div>
    );
}
