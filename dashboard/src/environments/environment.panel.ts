import {EnvironmentInterface} from "./environment-interface"


import {environment as ftmEnv} from "./environment.ftm_8"
import {environment as bnbEnv} from "./environment.bnb_8"
import {environment as bnb82Env} from "./environment.bnb_8_2"
import {environment as baseEnv} from "./environment.base_8"
import {environment as base82Env} from "./environment.base_8_2"

export const environment: EnvironmentInterface = {
    name: "panel",
    assetsFolder: "panel",
    serverUrl: "https://analytics-api.symmio.io",
    panel: true,
    environments: [
        ftmEnv,
        bnbEnv,
        baseEnv,
        bnb82Env,
        base82Env,
    ],
}