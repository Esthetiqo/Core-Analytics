import { EnvironmentInterface } from "./environment-interface";
import { environment as core82Env } from "./environment.core-8_2";

export const environment: EnvironmentInterface = {
  name: "Core",
  assetsFolder: "core",
  singleAffiliateAccountSource: "0xd6ee1fd75d11989e57B57AA6Fd75f558fBf02a5e",
  environments: [core82Env],
};
