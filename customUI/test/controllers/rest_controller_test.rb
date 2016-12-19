require 'test_helper'

class RestControllerTest < ActionDispatch::IntegrationTest
  test "should get openhab_request" do
    get rest_openhab_request_url
    assert_response :success
  end

end
