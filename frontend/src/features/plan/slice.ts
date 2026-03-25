import {
  createEntityAdapter,
  createSelector,
  createSlice,
  type PayloadAction,
} from "@reduxjs/toolkit";
import type { Plan, PlanPatch } from "./entities";
import type { RootState } from "../../app/store";
import {
  createPlan,
  deletePlan,
  fetchAllPlansInProject,
  fetchPlan,
  patchPlan,
} from "./thunks";

const plansAdapter = createEntityAdapter<Plan, string>({
  selectId: (project) => project.id,
  sortComparer: (a, b) => a.dtUpdated.localeCompare(b.dtUpdated),
});
const plansSelectors = plansAdapter.getSelectors<RootState>(
  (state) => state.plans,
);

const plansSlice = createSlice({
  name: "plans",
  initialState: plansAdapter.getInitialState(),
  reducers: {
    optimisticPatchPlan: (
      state,
      action: PayloadAction<{ id: string; patch: PlanPatch }>,
    ) => {
      const payload = action.payload;
      plansAdapter.updateOne(state, {
        id: payload.id,
        changes: payload.patch,
      });
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(createPlan.fulfilled, (state, action) => {
        plansAdapter.addOne(state, action.payload);
      })
      .addCase(deletePlan.fulfilled, (state, action) => {
        plansAdapter.removeOne(state, action.meta.arg);
      })
      .addCase(patchPlan.rejected, () => {
        // TODO: fix conflict
      })
      .addCase(fetchPlan.fulfilled, (state, action) => {
        plansAdapter.addOne(state, action.payload);
      })
      .addCase(fetchAllPlansInProject.fulfilled, (state, action) => {
        const newPlans = action.payload.filter(
          (plan) => !state.entities[plan.id],
        );
        plansAdapter.addMany(state, newPlans);
      });
  },
});

export const selectPlanById = plansSelectors.selectById;
export const selectAllPlans = plansSelectors.selectAll;
export const selectPlansByProjectId = (projectId: string) =>
  createSelector([selectAllPlans], (plans) =>
    plans.filter((plan) => plan.projectId === projectId),
  );

export const { optimisticPatchPlan } = plansSlice.actions;
export default plansSlice.reducer;
