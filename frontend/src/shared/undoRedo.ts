export interface Action {
  reversed(): Action;
}

export class UndoRedo<T extends Action> {
  private done: T[] = [];
  private undone: T[] = [];

  do(action: T) {
    this.done.push(action);
  }

  undo(): Action {
    const last = this.done.pop();
    if (last) {
      this.undone.push(last);
      return last.reversed();
    } else {
      throw Error("cannot undo: no actions");
    }
  }

  redo(): Action {
    const last = this.undone.pop();
    if (last) {
      this.done.push(last);
      return last;
    } else {
      throw Error("cannot redo: no actions");
    }
  }

  canUndo(): boolean {
    return this.done.length !== 0;
  }

  canRedo(): boolean {
    return this.undone.length !== 0;
  }
}
