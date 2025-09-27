"use client";
import React from "react";
import Dither from "../Dither";

interface DitherBackgroundProps {
    variant?: "vibrant" | "subtle" | "minimal";
    className?: string;
}

export default function DitherBackground({
    variant = "vibrant",
    className = "",
}: DitherBackgroundProps) {
    // Convert hex colors to RGB values (0-1 range)
    const hexToRgb = (hex: string): [number, number, number] => {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result
            ? [
                  parseInt(result[1], 16) / 255,
                  parseInt(result[2], 16) / 255,
                  parseInt(result[3], 16) / 255,
              ]
            : [0, 0, 0];
    };

    // Theme colors from globals.css
    const themeColors = {
        vibrant: {
            // Using citrus-500 (#fa8b2a) as primary wave color
            waveColor: hexToRgb("#fa8b2a"),
            colorNum: 8,
            waveAmplitude: 0.001,
            waveFrequency: 0.5,
            waveSpeed: 0.05,
            mouseRadius: 0.4,
        },
        subtle: {
            // Using cream-200 (#f8f0e3) as base with citrus accents
            waveColor: hexToRgb("#f8f0e3"),
            colorNum: 4,
            waveAmplitude: 0.5,
            waveFrequency: 1,
            waveSpeed: 0.07,
            mouseRadius: 0.6,
        },
        minimal: {
            // Using stone-400 (#a0a0a0) for minimal effect
            waveColor: hexToRgb("#a0a0a0"),
            colorNum: 3,
            waveAmplitude: 0.15,
            waveFrequency: 2,
            waveSpeed: 2,
            mouseRadius: 0.8,
        },
    };

    const config = themeColors[variant];

    return (
        <div className={`absolute inset-0 w-full h-full ${className}`}>
            <Dither
                waveColor={config.waveColor}
                disableAnimation={false}
                enableMouseInteraction={true}
                mouseRadius={config.mouseRadius}
                colorNum={config.colorNum}
                waveAmplitude={config.waveAmplitude}
                waveFrequency={config.waveFrequency}
                waveSpeed={config.waveSpeed}
                pixelSize={1.5}
            />
        </div>
    );
}
