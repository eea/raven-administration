import axios from "axios";
import ErrorParser from './error.parser';
import Eventy from "../helpers/eventy"

const Request = async (payload) => {
    try {
        Eventy.showProgress();
        const response = await axios(payload);
        Eventy.hideProgress();
        return response.data
    }
    catch (error) {
        console.log("EEEERRROR", error);
        const message = ErrorParser.asMessage(error);
        Eventy.failProgress();
        Eventy.showHideMessage("Error", message, "error", 60000);
        throw new Error(message);
    }
};

export default Request;