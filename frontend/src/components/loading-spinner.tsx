import './loading-spinner.css';

interface LoadingSpinnerProps {
    size?: number;
    color?: string;
    borderWidth?: number;
}

export function LoadingSpinner({
    size = 40,
    color = '#3B82F6',
    borderWidth = 4,
}: LoadingSpinnerProps) {
    return (
        <div
            className="loading-spinner"
            style={{
                width: size,
                height: size,
                borderWidth,
                borderColor: `${color} transparent transparent transparent`,
            }}
        />
    );
}
