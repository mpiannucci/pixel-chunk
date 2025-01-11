interface ColorPickerProps {
    selectedColor: string;
    onColorChange: (color: string) => void;
}

export function ColorPicker({
    selectedColor,
    onColorChange,
}: ColorPickerProps) {
    return (
        <div className="flex items-center">
            <label htmlFor="colorPicker" className="mr-2">
                Color:
            </label>
            <input
                type="color"
                id="colorPicker"
                value={selectedColor}
                onChange={(e) => onColorChange(e.target.value)}
                className="w-10 h-10 rounded cursor-pointer"
            />
            <span className="ml-2">{selectedColor}</span>
        </div>
    );
}
