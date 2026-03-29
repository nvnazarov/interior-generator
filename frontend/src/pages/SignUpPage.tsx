import { Center, Page } from "../shared/components";
import { SignUpForm } from "../slices/account";

export function SignUpPage() {
  return (
    <Page>
      <Center>
        <SignUpForm />
      </Center>
    </Page>
  );
}
