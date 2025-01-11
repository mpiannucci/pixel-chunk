import { DrawState } from '@/state';

interface GridProps {
    state: DrawState;
    editMode: boolean;
    onPixelClick: (index: number) => void;
}

export function Grid({ state, editMode, onPixelClick }: GridProps) {
    const gridSize = state.cols;

    return (
        <div
            className="grid gap-px mb-4 bg-gray-200"
            style={{
                gridTemplateColumns: `repeat(${gridSize}, minmax(0, 1fr))`,
                width: `${gridSize * 1.5}rem`,
                height: `${gridSize * 1.5}rem`,
            }}
        >
            {state.chunks.map((color, index) => (
                <div
                    key={`${index}`}
                    className="bg-white hover:opacity-90 transition-opacity"
                    style={{
                        backgroundColor: color || 'white',
                        cursor: editMode ? 'pointer' : 'default',
                    }}
                    onClick={() => onPixelClick(index)}
                />
            ))}
        </div>
    );
}
