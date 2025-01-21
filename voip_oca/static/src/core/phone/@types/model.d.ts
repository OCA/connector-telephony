declare module "models" {
  import {Call as CallClass} from "@voip_oca/core/phone/call_model";

  export interface Call extends CallClass {}
  export interface Thread {
    recipients: Follower[];
  }

  export interface Models {
    Call: Call;
  }
}
