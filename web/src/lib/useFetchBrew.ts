import {useState} from 'react';

export interface BrewApiData {
  name: string[];
  desc: string;
  homepage: string;
  version: string;
  url: string;
  deprecated?: boolean;
  deprecation_reason?: string;
  caveats?: string;
}

export const useFetchBrew = () => {
  const [brewData, setBrewData] = useState<BrewApiData | null>(null);
  const [loadingBrew, setLoadingBrew] = useState(false);

  const fetchBrewData = async (bundleName: string, type: string) => {
    if (type !== 'cask' && type !== 'brew') return;

    setLoadingBrew(true);
    try {
      const endpoint = type === 'cask' ? 'cask' : 'formula';
      const response = await fetch(`https://formulae.brew.sh/api/${endpoint}/${bundleName}.json`);
      if (response.ok) {
        const data = await response.json();
        setBrewData(data);
      }
    } catch (error) {
      console.warn('Failed to fetch Homebrew data:', error);
    } finally {
      setLoadingBrew(false);
    }
  };

  return {brewData, loadingBrew, fetchBrewData};
};
