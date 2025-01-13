interface GridProps {
    colors: string[];
    cols: number;
    rows: number;
    conflictedIndices: number[];
    conflictedColor: string;
    editMode: boolean;
    onPixelClick: (index: number) => void;
}

export function Grid({
    colors,
    cols,
    rows,
    conflictedIndices,
    conflictedColor,
    editMode,
    onPixelClick,
}: GridProps) {
    return (
        <div
            className="grid gap-px bg-gray-200 flex-1"
            style={{
                gridTemplateColumns: `repeat(${cols}, 1fr)`,
                gridTemplateRows: `repeat(${rows}, 1fr)`,
            }}
        >
            {colors.map((color, index) => {
                const hasConflict = conflictedIndices.includes(index);
                return (
                    <div
                        key={`${index}`}
                        className="hover:opacity-90 transition-opacity"
                        style={{
                            backgroundColor: color || 'white',
                            cursor: editMode ? 'pointer' : 'default',
                            boxShadow: hasConflict
                                ? `0 0 0 3px ${conflictedColor} inset`
                                : 'none',
                        }}
                        onClick={() => onPixelClick(index)}
                    />
                );
            })}
        </div>
    );
}
