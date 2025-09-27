"use client";

import { useEffect, useRef } from "react";

interface IframeEmbedProps {
    agentId?: string;
    organizationId?: string;
    width?: number | string;
    height?: number | string;
    className?: string;
    style?: React.CSSProperties;
}

export default function IframeEmbed({
    agentId,
    organizationId,
    width = 350,
    height = 500,
    className,
    style,
}: IframeEmbedProps) {
    const iframeRef = useRef<HTMLIFrameElement>(null);

    useEffect(() => {
        const iframe = iframeRef.current;
        if (!iframe) return;

        const handleMessage = (event: MessageEvent) => {
            const allowedOrigins = [
                window.location.origin,
                process.env.NEXT_PUBLIC_EMBED_ORIGIN || window.location.origin,
            ];

            if (!allowedOrigins.includes(event.origin)) {
                return;
            }

            switch (event.data.type) {
                case "EMBED_RESIZE":
                    if (iframe && event.data.height) {
                        iframe.style.height = `${event.data.height}px`;
                    }
                    break;
                case "EMBED_READY":
                    console.log("Embed widget is ready");
                    break;
                case "EMBED_CLOSE":
                    if (iframe) {
                        iframe.style.display = "none";
                    }
                    break;
                default:
                    break;
            }
        };

        window.addEventListener("message", handleMessage);

        return () => {
            window.removeEventListener("message", handleMessage);
        };
    }, []);

    const getEmbedUrl = () => {
        const baseUrl = `${window.location.origin}/embed`;
        const params = new URLSearchParams();

        if (agentId) params.append("agentId", agentId);
        if (organizationId) params.append("orgId", organizationId);

        return `${baseUrl}?${params.toString()}`;
    };

    return (
        <iframe
            ref={iframeRef}
            src={getEmbedUrl()}
            width={width}
            height={height}
            className={`embed-iframe-container ${className || ""}`}
            style={{
                border: "none",
                borderRadius: "12px",
                boxShadow: "0 10px 40px rgba(0, 0, 0, 0.15)",
                ...style,
            }}
            title="AI Assistant Chat Widget"
            allow="microphone; camera"
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
        />
    );
}

export function generateEmbedScript(config: {
    agentId?: string;
    organizationId?: string;
    domain: string;
    width?: number | string;
    height?: number | string;
}) {
    return `
<!-- Supportify Embed Widget -->
<div id="supportify-embed-container"></div>
<script>
(function() {
  var iframe = document.createElement('iframe');
  iframe.src = '${config.domain}/embed?${new URLSearchParams({
        ...(config.agentId && { agentId: config.agentId }),
        ...(config.organizationId && { orgId: config.organizationId }),
    }).toString()}';
  iframe.width = '${config.width || 350}';
  iframe.height = '${config.height || 500}';
  iframe.style.border = 'none';
  iframe.style.borderRadius = '12px';
  iframe.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.15)';
  iframe.style.position = 'fixed';
  iframe.style.bottom = '20px';
  iframe.style.right = '20px';
  iframe.style.zIndex = '9999';
  iframe.title = 'AI Assistant Chat Widget';
  iframe.allow = 'microphone; camera';
  iframe.sandbox = 'allow-scripts allow-same-origin allow-forms allow-popups';
  
  var container = document.getElementById('supportify-embed-container');
  if (container) {
    container.appendChild(iframe);
  } else {
    document.body.appendChild(iframe);
  }
})();
</script>
`;
}
