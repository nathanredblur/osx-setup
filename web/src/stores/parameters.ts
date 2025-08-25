import type {AppParameterValues, Parameter, ParameterValues} from '@/types/data.d.ts';
import {create} from 'zustand';
import {persist, subscribeWithSelector} from 'zustand/middleware';

interface ParametersState {
  values: AppParameterValues;
  validationState: Record<string, {isValid: boolean; errors: string[]}>;
  setParameter: (appId: string, paramName: string, value: string) => void;
  getParameters: (appId: string) => ParameterValues;
  validateApp: (appId: string, parameters: Parameter[]) => string[];
  hasRequiredParameters: (appId: string, parameters: Parameter[]) => boolean;
  updateValidationState: (appId: string, isValid: boolean, errors: string[]) => void;
  getValidationState: (appId: string) => {isValid: boolean; errors: string[]};
  clearApp: (appId: string) => void;
  clearAll: () => void;
}

export const useParametersStore = create<ParametersState>()(
  subscribeWithSelector(
    persist(
      (set, get) => ({
        values: {},
        validationState: {},

        setParameter: (appId: string, paramName: string, value: string) => {
          const current = {...get().values};
          if (!current[appId]) {
            current[appId] = {};
          }
          current[appId][paramName] = value;
          set({values: current});
        },

        getParameters: (appId: string) => {
          return get().values[appId] || {};
        },

        validateApp: (appId: string, parameters: Parameter[]) => {
          const errors: string[] = [];
          const values = get().values[appId] || {};

          for (const param of parameters) {
            if (param.required && (!values[param.name] || values[param.name].trim() === '')) {
              errors.push(`${param.description} is required`);
            }

            // Validate email format
            if (param.type === 'email' && values[param.name]) {
              const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
              if (!emailRegex.test(values[param.name])) {
                errors.push(`${param.description} must be a valid email address`);
              }
            }

            // Validate number format
            if (param.type === 'number' && values[param.name]) {
              if (isNaN(Number(values[param.name]))) {
                errors.push(`${param.description} must be a valid number`);
              }
            }
          }

          return errors;
        },

        hasRequiredParameters: (appId: string, parameters: Parameter[]) => {
          const values = get().values[appId] || {};
          const requiredParams = parameters.filter(p => p.required);

          return requiredParams.every(
            param => values[param.name] && values[param.name].trim() !== ''
          );
        },

        updateValidationState: (appId: string, isValid: boolean, errors: string[]) => {
          const current = {...get().validationState};
          current[appId] = {isValid, errors};
          set({validationState: current});
        },

        getValidationState: (appId: string) => {
          return get().validationState[appId] || {isValid: true, errors: []};
        },

        clearApp: (appId: string) => {
          const currentValues = {...get().values};
          const currentValidation = {...get().validationState};
          delete currentValues[appId];
          delete currentValidation[appId];
          set({values: currentValues, validationState: currentValidation});
        },

        clearAll: () => set({values: {}, validationState: {}}),
      }),
      {name: 'store.parameters'}
    )
  )
);
