interface GridProps {
    colors: string[];
    cols: number;
    editMode: boolean;
    onPixelClick: (index: number) => void;
}

export function Grid({ colors, cols, editMode, onPixelClick }: GridProps) {
    return (
        <div
            className="grid gap-px mb-4 bg-gray-200"
            style={{
                gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
                width: `${cols * 1.5}rem`,
                height: `${cols * 1.5}rem`,
            }}
        >
            {colors.map((color, index) => (
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
