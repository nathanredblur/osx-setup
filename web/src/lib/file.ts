export async function saveTextFile(filename: string, content: string) {
  const supportsFS = 'showSaveFilePicker' in window;
  if (supportsFS) {
    // @ts-expect-error: FS API types not in lib by default
    const handle: FileSystemFileHandle = await window.showSaveFilePicker({
      suggestedName: filename,
      types: [{description: 'Text', accept: {'text/plain': ['.sh']}}],
    });
    const writable = await handle.createWritable();
    await writable.write(content);
    await writable.close();
    return;
  }
  const blob = new Blob([content], {type: 'text/plain'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
