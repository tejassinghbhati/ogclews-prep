import { useState, useCallback } from 'react';
import { DEFAULT_MACRO_PARAMS, DEFAULT_CLEWS_PARAMS } from '../constants/modelConstants';

function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

export function useParameterState() {
  const [macroParams, setMacroParams] = useState(() => deepClone(DEFAULT_MACRO_PARAMS));
  const [clewsParams, setClewsParams] = useState(() => deepClone(DEFAULT_CLEWS_PARAMS));

  const updateMacro = useCallback((key, value) => {
    setMacroParams(prev => ({
      ...prev,
      [key]: { ...prev[key], value },
    }));
  }, []);

  const updateClews = useCallback((key, value) => {
    setClewsParams(prev => ({
      ...prev,
      [key]: { ...prev[key], value },
    }));
  }, []);

  const resetAll = useCallback(() => {
    setMacroParams(deepClone(DEFAULT_MACRO_PARAMS));
    setClewsParams(deepClone(DEFAULT_CLEWS_PARAMS));
  }, []);

  return { macroParams, clewsParams, updateMacro, updateClews, resetAll };
}
