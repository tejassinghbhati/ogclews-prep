import { useMemo } from 'react';
import { CONVERGENCE_EPSILON, MAX_ITERATIONS } from '../constants/modelConstants';

export function useConvergenceState(messages) {
  return useMemo(() => {
    const history = [];
    let iteration = 0;
    let isConverged = false;

    messages.forEach(msg => {
      const text = msg.text;

      // Parse iteration number
      const iterMatch = text.match(/Iteration\s+(\d+)/i);
      if (iterMatch) {
        iteration = parseInt(iterMatch[1], 10);
      }

      // Parse delta values
      const deltaTauMatch = text.match(/delta_tau[_a-z]*\s*[=:]\s*([\d.eE+\-]+)/i);
      const tauCMatch = text.match(/tau_c\s*[=:]\s*([\d.eE+\-]+)/i);
      const alphaGMatch = text.match(/alpha_G\s*[=:]\s*([\d.eE+\-]+)/i);
      const l2Match = text.match(/(?:delta|norm|L2)\s*[=:]\s*([\d.eE+\-]+)/i);

      if (iterMatch || deltaTauMatch || l2Match) {
        const entry = {
          iter: iteration,
          delta_tau: deltaTauMatch ? parseFloat(deltaTauMatch[1]) : null,
          tau_c: tauCMatch ? parseFloat(tauCMatch[1]) : null,
          alpha_G: alphaGMatch ? parseFloat(alphaGMatch[1]) : null,
          l2norm: l2Match ? parseFloat(l2Match[1]) : null,
          timestamp: msg.timestamp,
        };
        // Only push if we have meaningful data
        if (entry.delta_tau !== null || entry.l2norm !== null) {
          history.push(entry);
        }
      }

      if (text.toLowerCase().includes('converged') || text.includes('[CONVERGED]')) {
        isConverged = true;
      }
    });

    // Derive convergence percent from l2norm trend
    const currentDelta = history.length > 0 ? (history[history.length - 1].l2norm ?? history[history.length - 1].delta_tau) : null;
    const firstDelta = history.length > 0 ? (history[0].l2norm ?? history[0].delta_tau) : null;
    const convergencePct = (firstDelta && currentDelta)
      ? Math.min(100, Math.max(0, (1 - currentDelta / firstDelta) * 100))
      : 0;

    return { iteration, history, currentDelta, isConverged, convergencePct, maxIter: MAX_ITERATIONS, epsilon: CONVERGENCE_EPSILON };
  }, [messages]);
}
