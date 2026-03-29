import { Center, Page } from "../shared/components";
import { SignInForm } from "../slices/account";

export function SignInPage() {
  return (
    <Page>
      <Center>
        <SignInForm />
      </Center>
    </Page>
  );
}
