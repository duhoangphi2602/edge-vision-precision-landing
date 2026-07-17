# Failure Case Analysis
*Generated for Day 17*

## Error Categories
1. **Target Lost:** Background clutter, extreme pose, low lighting.
2. **False Positive:** ID misclassification.
3. **Stale Data:** Compute delay causing >200ms latency.

## Limitations
- Tracker assumes target does not leave frame completely for >1s.
- Stale threshold set at 200ms for safety.
