import "./SignInPage.scss";
import { SignInForm } from "../../slices/account/components";

export function SignInPage() {
  return (
    <div className="sign-in-page">
      <SignInForm />
    </div>
  );
}
