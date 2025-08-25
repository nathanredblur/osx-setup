import {useParametersStore} from '@/stores/parameters';
import type {Parameter} from '@/types/data.d.ts';
import React, {useEffect, useState} from 'react';

interface Props {
  appId: string;
  parameters: Parameter[];
  onValidationChange?: (isValid: boolean, errors: string[]) => void;
}

const ParameterForm: React.FC<Props> = ({appId, parameters, onValidationChange}) => {
  const {setParameter, getParameters, validateApp, updateValidationState} = useParametersStore();
  const [localValues, setLocalValues] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<string[]>([]);

  // Initialize local values with store values and defaults
  useEffect(() => {
    const storeValues = getParameters(appId);
    const initialValues: Record<string, string> = {};

    parameters.forEach(param => {
      initialValues[param.name] = storeValues[param.name] || param.default || '';
    });

    setLocalValues(initialValues);
  }, [appId, parameters, getParameters]);

  // Validate and update parent component and store
  useEffect(() => {
    const validationErrors = validateApp(appId, parameters);
    const isValid = validationErrors.length === 0;
    setErrors(validationErrors);
    onValidationChange?.(isValid, validationErrors);
    updateValidationState(appId, isValid, validationErrors);
  }, [localValues, appId, parameters, validateApp, onValidationChange, updateValidationState]);

  const handleInputChange = (paramName: string, value: string) => {
    setLocalValues(prev => ({...prev, [paramName]: value}));
    setParameter(appId, paramName, value);
  };

  const getInputType = (paramType: Parameter['type']) => {
    switch (paramType) {
      case 'email':
        return 'email';
      case 'number':
        return 'number';
      case 'boolean':
        return 'checkbox';
      default:
        return 'text';
    }
  };

  const renderInput = (param: Parameter) => {
    const value = localValues[param.name] || '';
    const hasError = errors.some(error => error.includes(param.description));

    if (param.type === 'boolean') {
      return (
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id={`param-${param.name}`}
            checked={value === 'true'}
            onChange={e => handleInputChange(param.name, e.target.checked ? 'true' : 'false')}
            className="rounded border-neutral-300 text-blue-600 focus:ring-blue-500 dark:border-neutral-600 dark:bg-neutral-800"
          />
          <label htmlFor={`param-${param.name}`} className="text-sm">
            {param.description}
            {param.required && <span className="ml-1 text-red-500">*</span>}
          </label>
        </div>
      );
    }

    return (
      <div className="space-y-1">
        <label htmlFor={`param-${param.name}`} className="block text-sm font-medium">
          {param.description}
          {param.required && <span className="ml-1 text-red-500">*</span>}
        </label>
        <input
          type={getInputType(param.type)}
          id={`param-${param.name}`}
          value={value}
          onChange={e => handleInputChange(param.name, e.target.value)}
          placeholder={param.default || ''}
          className={`w-full rounded-md border px-3 py-2 text-sm focus:ring-2 focus:outline-none ${
            hasError
              ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
              : 'border-neutral-300 focus:border-blue-500 focus:ring-blue-500'
          } dark:border-neutral-600 dark:bg-neutral-800 dark:text-white`}
        />
        {param.default && <p className="text-xs text-neutral-500">Default: {param.default}</p>}
      </div>
    );
  };

  if (parameters.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4 rounded-md border border-neutral-200 p-4 dark:border-neutral-800">
      <div className="flex items-center gap-2">
        <div className="h-2 w-2 rounded-full bg-blue-500"></div>
        <h4 className="text-sm font-medium">Configuration Parameters</h4>
      </div>

      <div className="space-y-3">
        {parameters.map(param => (
          <div key={param.name}>{renderInput(param)}</div>
        ))}
      </div>

      {errors.length > 0 && (
        <div className="rounded-md bg-red-50 p-3 dark:bg-red-900/20">
          <div className="text-sm text-red-800 dark:text-red-200">
            <div className="mb-1 font-medium">Please fix the following errors:</div>
            <ul className="list-inside list-disc space-y-1">
              {errors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParameterForm;
