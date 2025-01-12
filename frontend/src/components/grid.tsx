interface GridProps {
    colors: string[];
    cols: number;
    conflicted_indices: number[];
    conflicted_color: string;
    editMode: boolean;
    onPixelClick: (index: number) => void;
}

export function Grid({
    colors,
    cols,
    conflicted_indices,
    conflicted_color,
    editMode,
    onPixelClick,
}: GridProps) {
    return (
        <div
            className="grid gap-px mb-4 bg-gray-200"
            style={{
                gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
                width: `${cols * 1.5}rem`,
                height: `${cols * 1.5}rem`,
            }}
        >
            {colors.map((color, index) => {
                const hasConflict = conflicted_indices.includes(index);
                return (
                    <div
                        key={`${index}`}
                        className="bg-white hover:opacity-90 transition-opacity"
                        style={{
                            backgroundColor: color || 'white',
                            cursor: editMode ? 'pointer' : 'default',
                            boxShadow: hasConflict ? `0 0 0 3px ${conflicted_color} inset` : 'none',

                        }}
                        onClick={() => onPixelClick(index)}
                    />
                );
            })}
        </div>
    );
}
