const ErrorParser = {
  asMessage: function (error) {
    let message = "Unknown error";
    if (error.response.status == 404) message = "Route not found";
    else if (error.response.status == 400) {
      let errMsg = error.response.data.msg;
      message = JSON.stringify(errMsg);
    } else {
      message = error.response.data.msg;
      if (!message) message = "Something went wrong!";
    }
    return message;
  }
};

export default ErrorParser;
