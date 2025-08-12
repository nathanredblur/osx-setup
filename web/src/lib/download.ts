import type {ProgramMeta} from '@/types/data.d.ts';
import JSZip from 'jszip';
import {createBrewfile, createCustomInstall, createPostConfig} from './bundle';

// Function to download a file
export function downloadFile(
  content: string,
  filename: string,
  mimeType: string = 'text/plain'
): void {
  const blob = new Blob([content], {type: mimeType});
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');

  link.href = url;
  link.download = filename;
  link.style.display = 'none';

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  URL.revokeObjectURL(url);
}

// Function to get the content of macSnap.sh file
export async function getMacSnapContent(): Promise<string> {
  try {
    const response = await fetch('/assets/macSnap.sh');
    if (!response.ok) {
      throw new Error('Failed to fetch macSnap.sh');
    }
    return await response.text();
  } catch (error) {
    console.error('Error fetching macSnap.sh:', error);
    // Fallback content if the file cannot be loaded
    return `#!/bin/bash
echo "🚀 MacSnap Setup - Basic Version"
echo "Please download the complete macSnap.sh from the repository"
`;
  }
}

// Function to get the content of README.md
export async function getReadmeContent(): Promise<string> {
  try {
    const response = await fetch('/assets/README.md');
    if (!response.ok) {
      throw new Error('Failed to fetch README.md');
    }
    return await response.text();
  } catch (error) {
    console.error('Error fetching README.md:', error);
    // Fallback content if the file cannot be loaded
    return `# MacSnap Setup Files

This package contains all the necessary files to set up your Mac.

Please download the complete README.md from the repository.
`;
  }
}

// Function to download the Brewfile
export function downloadBrewfile(programs: ProgramMeta[]): void {
  const content = createBrewfile(programs);
  downloadFile(content, 'Brewfile', 'text/plain');
}

// Function to download postConfig.sh
export function downloadPostConfig(programs: ProgramMeta[]): void {
  const content = createPostConfig(programs);
  downloadFile(content, 'postConfig.sh', 'text/x-shellscript');
}

// Function to download customInstall.sh
export function downloadCustomInstall(programs: ProgramMeta[]): void {
  const content = createCustomInstall(programs);
  downloadFile(content, 'customInstall.sh', 'text/x-shellscript');
}

// Function to download macSnap.sh
export async function downloadMacSnap(): Promise<void> {
  const content = await getMacSnapContent();
  downloadFile(content, 'macSnap.sh', 'text/x-shellscript');
}

// Function to create a ZIP file with all files
export async function downloadAllAsZip(programs: ProgramMeta[]): Promise<void> {
  try {
    const zip = new JSZip();

    // Add all files to the ZIP
    zip.file('Brewfile', createBrewfile(programs));
    zip.file('postConfig.sh', createPostConfig(programs));
    zip.file('customInstall.sh', createCustomInstall(programs));

    // Add macSnap.sh (main script)
    const macSnapContent = await getMacSnapContent();
    zip.file('macSnap.sh', macSnapContent);

    // Add static README
    const readmeContent = await getReadmeContent();
    zip.file('README.md', readmeContent);

    // Generate the ZIP and download it
    const content = await zip.generateAsync({type: 'blob'});
    const url = URL.createObjectURL(content);
    const link = document.createElement('a');

    link.href = url;
    link.download = `macsnap-setup-${new Date().toISOString().split('T')[0]}.zip`;
    link.style.display = 'none';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error creating ZIP file:', error);
    alert('Error creating ZIP file. Please download the files individually.');
  }
}
