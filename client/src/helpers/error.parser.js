const ErrorParser = {
  asMessage: function (error) {
    let message = "Unknown error";
    
    // Handle 404
    if (error.response?.status == 404) {
      message = "Route not found";
    } 
    // Handle 400 validation errors
    else if (error.response?.status == 400) {
      if (error.response.data instanceof Blob) {
        message = "File error: Could not parse input data";
      } else {
        // Extract the message - support both "msg" and "error" keys for backward compatibility
        message = error.response.data.msg || error.response.data.error || "Bad request";
      }
    } 
    // Handle other errors
    else if (error.response) {
      console.log("Error response: ", error.response);
      message = error.response.data?.msg || error.response.data?.error || "Something went wrong!";
    }
    // Handle network errors
    else if (error.request) {
      message = "Network error: Unable to reach server";
    }
    // Handle other errors
    else {
      message = error.message || "Unknown error occurred";
    }
    
    return message;
  }
};

export default ErrorParser;
