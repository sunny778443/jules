"""
Neuron models for synthetic brain architecture.
Includes Leaky Integrate-and-Fire (LIF), Adaptive Exponential LIF (AdEx), and Hodgkin-Huxley formulations.
"""

import math
from typing import List, Dict, Any, Optional, Tuple


class LIFNeuron:
    """
    Leaky Integrate-and-Fire (LIF) Neuron Model.
    Simulates membrane potential dynamics subject to leak and synaptic currents.
    """
    def __init__(
        self,
        neuron_id: str,
        v_rest: float = -70.0,
        v_thresh: float = -55.0,
        v_reset: float = -75.0,
        tau_m: float = 20.0,
        r_membrane: float = 10.0,
        refractory_period: float = 2.0
    ):
        self.neuron_id = neuron_id
        self.v_rest = v_rest
        self.v_thresh = v_thresh
        self.v_reset = v_reset
        self.tau_m = tau_m  # Membrane time constant (ms)
        self.r_membrane = r_membrane  # Membrane resistance (M-Ohm)
        self.refractory_period = refractory_period  # Refractory period (ms)

        self.v = v_rest
        self.refractory_timer = 0.0
        self.spike_history: List[float] = []

    def step(self, i_syn: float, dt: float = 1.0, current_time: float = 0.0) -> bool:
        """
        Advance membrane dynamics by time step dt (ms).
        Returns True if a spike occurs.
        """
        if self.refractory_timer > 0:
            self.refractory_timer -= dt
            self.v = self.v_reset
            return False

        # dV/dt = (-(V - V_rest) + R * I) / tau_m
        dv = (-(self.v - self.v_rest) + self.r_membrane * i_syn) / self.tau_m * dt
        self.v += dv

        if self.v >= self.v_thresh:
            self.v = self.v_reset
            self.refractory_timer = self.refractory_period
            self.spike_history.append(current_time)
            return True

        return False

    def reset(self):
        self.v = self.v_rest
        self.refractory_timer = 0.0
        self.spike_history.clear()


class AdExNeuron:
    """
    Adaptive Exponential Leaky Integrate-and-Fire (AdEx) Neuron Model.
    Captures spike-frequency adaptation, bursting, and subthreshold oscillations.
    """
    def __init__(
        self,
        neuron_id: str,
        v_rest: float = -70.0,
        v_reset: float = -60.0,
        v_thresh: float = -50.0,
        delta_t: float = 2.0,
        c_m: float = 200.0,      # Membrane capacitance (pF)
        g_l: float = 10.0,       # Leak conductance (nS)
        a: float = 2.0,          # Subthreshold adaptation (nS)
        b: float = 10.0,         # Spike-triggered adaptation (pA)
        tau_w: float = 30.0,     # Adaptation time constant (ms)
        v_peak: float = 0.0
    ):
        self.neuron_id = neuron_id
        self.v_rest = v_rest
        self.v_reset = v_reset
        self.v_thresh = v_thresh
        self.delta_t = delta_t
        self.c_m = c_m
        self.g_l = g_l
        self.a = a
        self.b = b
        self.tau_w = tau_w
        self.v_peak = v_peak

        self.v = v_rest
        self.w = 0.0  # Adaptation current
        self.spike_history: List[float] = []

    def step(self, i_syn: float, dt: float = 1.0, current_time: float = 0.0) -> bool:
        """Advance AdEx state equations."""
        # Exponential term
        exp_term = self.delta_t * math.exp(min((self.v - self.v_thresh) / self.delta_t, 10.0))
        dv = (-self.g_l * (self.v - self.v_rest) + self.g_l * exp_term - self.w + i_syn) / self.c_m * dt
        dw = (self.a * (self.v - self.v_rest) - self.w) / self.tau_w * dt

        self.v += dv
        self.w += dw

        if self.v >= self.v_peak:
            self.v = self.v_reset
            self.w += self.b
            self.spike_history.append(current_time)
            return True

        return False

    def reset(self):
        self.v = self.v_rest
        self.w = 0.0
        self.spike_history.clear()


class HodgkinHuxleyNeuron:
    """
    Biophysically detailed Hodgkin-Huxley neuron model.
    Models voltage-gated Na+ and K+ ion channel dynamics.
    """
    def __init__(
        self,
        neuron_id: str,
        v_rest: float = -65.0,
        c_m: float = 1.0,      # uF/cm^2
        g_na: float = 120.0,   # mS/cm^2
        g_k: float = 36.0,     # mS/cm^2
        g_l: float = 0.3,      # mS/cm^2
        v_na: float = 50.0,    # mV
        v_k: float = -77.0,    # mV
        v_l: float = -54.38    # mV
    ):
        self.neuron_id = neuron_id
        self.c_m = c_m
        self.g_na = g_na
        self.g_k = g_k
        self.g_l = g_l
        self.v_na = v_na
        self.v_k = v_k
        self.v_l = v_l

        self.v = v_rest
        self.m = self._alpha_m(v_rest) / (self._alpha_m(v_rest) + self._beta_m(v_rest))
        self.h = self._alpha_h(v_rest) / (self._alpha_h(v_rest) + self._beta_h(v_rest))
        self.n = self._alpha_n(v_rest) / (self._alpha_n(v_rest) + self._beta_n(v_rest))

        self.spike_history: List[float] = []
        self._was_above = False

    @staticmethod
    def _alpha_m(v: float) -> float:
        x = (v + 40.0)
        if abs(x) < 1e-6:
            return 1.0
        return 0.1 * x / (1.0 - math.exp(-x / 10.0))

    @staticmethod
    def _beta_m(v: float) -> float:
        return 4.0 * math.exp(-(v + 65.0) / 18.0)

    @staticmethod
    def _alpha_h(v: float) -> float:
        return 0.07 * math.exp(-(v + 65.0) / 20.0)

    @staticmethod
    def _beta_h(v: float) -> float:
        return 1.0 / (1.0 + math.exp(-(v + 35.0) / 10.0))

    @staticmethod
    def _alpha_n(v: float) -> float:
        x = (v + 55.0)
        if abs(x) < 1e-6:
            return 0.1
        return 0.01 * x / (1.0 - math.exp(-x / 10.0))

    @staticmethod
    def _beta_n(v: float) -> float:
        return 0.125 * math.exp(-(v + 65.0) / 80.0)

    def step(self, i_inj: float, dt: float = 0.01, current_time: float = 0.0) -> bool:
        """
        Advance HH membrane potential using Euler integration.
        dt in ms (typically small e.g. 0.01-0.05 ms).
        """
        i_na = self.g_na * (self.m ** 3) * self.h * (self.v - self.v_na)
        i_k = self.g_k * (self.n ** 4) * (self.v - self.v_k)
        i_l = self.g_l * (self.v - self.v_l)

        dv = (i_inj - i_na - i_k - i_l) / self.c_m * dt
        dm = (self._alpha_m(self.v) * (1.0 - self.m) - self._beta_m(self.v) * self.m) * dt
        dh = (self._alpha_h(self.v) * (1.0 - self.h) - self._beta_h(self.v) * self.h) * dt
        dn = (self._alpha_n(self.v) * (1.0 - self.n) - self._beta_n(self.v) * self.n) * dt

        self.v += dv
        self.m += dm
        self.h += dh
        self.n += dn

        spiked = False
        if self.v >= 0.0 and not self._was_above:
            spiked = True
            self.spike_history.append(current_time)
            self._was_above = True
        elif self.v < 0.0:
            self._was_above = False

        return spiked
